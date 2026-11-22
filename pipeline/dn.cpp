// dn.cpp - temporal accumulation (static-camera groups, lighting-change rejection) + edge-avoiding a-trous filter
// usage: dn rawprefix outprefix plan.txt [K=6] [iters=5]
// plan.txt: one line per record, in order: "<recordIndex> <groupId>"  (groupId < 0: no temporal neighbours)
#include <cstdio>
#include <cstdlib>
#include <cmath>
#include <cstring>
#include <cstdint>
#include <vector>
#include <string>
#include <map>
#include <memory>
#include <algorithm>
#include <omp.h>
#include <immintrin.h>

static int W = 0, H = 0;
struct Frame {
  int idx, group;
  std::vector<float> irr, spec, nrm, dep, Pd, Ps, alb, E;
  std::vector<uint16_t> id;
};
static inline float lum3(const float* c) { return 0.2126f * c[0] + 0.7152f * c[1] + 0.0722f * c[2]; }

static std::shared_ptr<Frame> loadFrame(const std::string& prefix, int idx, int group) {
  char name[512]; snprintf(name, sizeof(name), "%s_%04d.bin", prefix.c_str(), idx);
  FILE* f = fopen(name, "rb");
  if (!f) { fprintf(stderr, "missing %s\n", name); exit(1); }
  int hdr[2]; if (fread(hdr, 4, 2, f) != 2) exit(1);
  W = hdr[0]; H = hdr[1];
  size_t n = (size_t)W * H;
  auto fr = std::make_shared<Frame>();
  fr->idx = idx; fr->group = group;
  std::vector<uint8_t> a8(n * 3); std::vector<int8_t> n8(n * 3); std::vector<uint16_t> h16(n * 3);
  fr->alb.resize(n * 3); fr->nrm.resize(n * 3); fr->dep.resize(n); fr->id.resize(n); fr->E.resize(n * 3); fr->irr.resize(n * 3); fr->spec.resize(n * 3);
  if (fread(a8.data(), 1, n * 3, f) != n * 3) exit(1);
  for (size_t i = 0; i < n * 3; i++) { float v = a8[i] / 255.0f; fr->alb[i] = v * v; }
  if (fread(n8.data(), 1, n * 3, f) != n * 3) exit(1);
  for (size_t i = 0; i < n * 3; i++) fr->nrm[i] = n8[i] / 127.0f;
  if (fread(fr->dep.data(), 4, n, f) != n) exit(1);
  if (fread(fr->id.data(), 2, n, f) != n) exit(1);
  float* dst[3] = {fr->E.data(), fr->irr.data(), fr->spec.data()};
  for (int k = 0; k < 3; k++) {
    if (fread(h16.data(), 2, n * 3, f) != n * 3) exit(1);
    for (size_t i = 0; i < n * 3; i++) dst[k][i] = _cvtsh_ss(h16[i]);
  }
  fclose(f);
  // prefiltered luminance (7x7, same id + normal) for lighting-change detection and firefly clamp
  fr->Pd.resize(n); fr->Ps.resize(n);
#pragma omp parallel for schedule(dynamic, 16)
  for (int y = 0; y < H; y++)
    for (int x = 0; x < W; x++) {
      size_t p = (size_t)y * W + x;
      const float* np_ = &fr->nrm[p * 3]; uint16_t ip = fr->id[p] & 0x7FFF;
      float sd = 0, ss = 0; int c = 0;
      for (int dy = -3; dy <= 3; dy++) {
        int yy = y + dy; if (yy < 0 || yy >= H) continue;
        for (int dx = -3; dx <= 3; dx++) {
          int xx = x + dx; if (xx < 0 || xx >= W) continue;
          size_t q = (size_t)yy * W + xx;
          if ((fr->id[q] & 0x7FFF) != ip) continue;
          const float* nq = &fr->nrm[q * 3];
          if (np_[0] * nq[0] + np_[1] * nq[1] + np_[2] * nq[2] < 0.9f) continue;
          sd += std::min(lum3(&fr->irr[q * 3]), 50.0f); ss += std::min(lum3(&fr->spec[q * 3]), 50.0f); c++;
        }
      }
      fr->Pd[p] = c ? sd / c : 0; fr->Ps[p] = c ? ss / c : 0;
    }
  // firefly clamp against the local mean
#pragma omp parallel for schedule(static)
  for (long long p = 0; p < (long long)n; p++) {
    float l = lum3(&fr->irr[p * 3]), lim = fr->Pd[p] * 6.0f + 0.3f;
    if (l > lim) { float s = lim / l; fr->irr[p * 3] *= s; fr->irr[p * 3 + 1] *= s; fr->irr[p * 3 + 2] *= s; }
    l = lum3(&fr->spec[p * 3]); lim = fr->Ps[p] * 6.0f + 0.3f;
    if (l > lim) { float s = lim / l; fr->spec[p * 3] *= s; fr->spec[p * 3 + 1] *= s; fr->spec[p * 3 + 2] *= s; }
  }
  return fr;
}

int main(int argc, char** argv) {
  if (argc < 4) { fprintf(stderr, "usage: dn rawprefix outprefix plan.txt [K] [iters]\n"); return 1; }
  std::string rawp = argv[1], outp = argv[2];
  int K = argc > 4 ? atoi(argv[4]) : 6, ITERS = argc > 5 ? atoi(argv[5]) : 5;
  std::vector<int> pidx, pgrp;
  { FILE* f = fopen(argv[3], "r"); if (!f) return 1; int a, b; while (fscanf(f, "%d %d", &a, &b) == 2) { pidx.push_back(a); pgrp.push_back(b); } fclose(f); }
  int NR = (int)pidx.size();
  std::map<int, std::shared_ptr<Frame>> cache;   // by plan position
  for (int i = 0; i < NR; i++) {
    double t0 = omp_get_wtime();
    int lo = i, hi = i;
    if (pgrp[i] >= 0) {
      while (lo > 0 && i - (lo - 1) <= K && pgrp[lo - 1] == pgrp[i]) lo--;
      while (hi < NR - 1 && (hi + 1) - i <= K && pgrp[hi + 1] == pgrp[i]) hi++;
    }
    for (auto it = cache.begin(); it != cache.end();) { if (it->first < lo) it = cache.erase(it); else ++it; }
    for (int j = lo; j <= hi; j++) if (!cache.count(j)) cache[j] = loadFrame(rawp, pidx[j], pgrp[j]);
    Frame& c = *cache[i];
    size_t n = (size_t)W * H;
    std::vector<float> ai(n * 3), as(n * 3), wi(n), ws(n);
    std::vector<float> aa(c.alb), ae(c.E), wa(n, 1.0f);
    for (size_t p = 0; p < n * 3; p++) { ai[p] = c.irr[p]; as[p] = c.spec[p]; }
    for (size_t p = 0; p < n; p++) { wi[p] = 1; ws[p] = 1; }
    for (int j = lo; j <= hi; j++) {
      if (j == i) continue;
      const Frame& o = *cache[j];
#pragma omp parallel for schedule(static)
      for (long long p = 0; p < (long long)n; p++) {
        if (o.id[p] != c.id[p] || (c.id[p] & 0x8000)) continue;
        float dz = fabsf(o.dep[p] - c.dep[p]); if (dz > 0.004f * c.dep[p] + 0.002f) continue;
        const float* a = &c.nrm[p * 3]; const float* b = &o.nrm[p * 3];
        if (a[0] * b[0] + a[1] * b[1] + a[2] * b[2] < 0.96f) continue;
        for (int k = 0; k < 3; k++) { aa[p * 3 + k] += o.alb[p * 3 + k]; ae[p * 3 + k] += o.E[p * 3 + k]; }
        wa[p] += 1.0f;
        float rd = fabsf(o.Pd[p] - c.Pd[p]) / (std::max(o.Pd[p], c.Pd[p]) + 0.03f);
        float w = rd <= 0.16f ? 1.0f : expf(-((rd - 0.16f) / 0.12f) * ((rd - 0.16f) / 0.12f));
        if (w > 0.01f) { ai[p * 3] += w * o.irr[p * 3]; ai[p * 3 + 1] += w * o.irr[p * 3 + 1]; ai[p * 3 + 2] += w * o.irr[p * 3 + 2]; wi[p] += w; }
        float rs = fabsf(o.Ps[p] - c.Ps[p]) / (std::max(o.Ps[p], c.Ps[p]) + 0.03f);
        float w2 = rs <= 0.30f ? 1.0f : expf(-((rs - 0.30f) / 0.2f) * ((rs - 0.30f) / 0.2f));
        if (w2 > 0.01f) { as[p * 3] += w2 * o.spec[p * 3]; as[p * 3 + 1] += w2 * o.spec[p * 3 + 1]; as[p * 3 + 2] += w2 * o.spec[p * 3 + 2]; ws[p] += w2; }
      }
    }
#pragma omp parallel for schedule(static)
    for (long long p = 0; p < (long long)n; p++) {
      float a = 1.0f / wi[p], b = 1.0f / ws[p];
      float ia = 1.0f / wa[p];
      for (int k = 0; k < 3; k++) { aa[p * 3 + k] *= ia; ae[p * 3 + k] *= ia; }
      ai[p * 3] *= a; ai[p * 3 + 1] *= a; ai[p * 3 + 2] *= a;
      as[p * 3] *= b; as[p * 3 + 1] *= b; as[p * 3 + 2] *= b;
    }
    // depth gradient
    std::vector<float> gz(n * 2);
#pragma omp parallel for schedule(static)
    for (int y = 0; y < H; y++)
      for (int x = 0; x < W; x++) {
        size_t p = (size_t)y * W + x;
        float gx = 0, gy = 0;
        if (x > 0 && x < W - 1 && ((c.id[p - 1] ^ c.id[p]) & 0x7FFF) == 0 && ((c.id[p + 1] ^ c.id[p]) & 0x7FFF) == 0) gx = (c.dep[p + 1] - c.dep[p - 1]) * 0.5f;
        if (y > 0 && y < H - 1 && ((c.id[p - W] ^ c.id[p]) & 0x7FFF) == 0 && ((c.id[p + W] ^ c.id[p]) & 0x7FFF) == 0) gy = (c.dep[p + W] - c.dep[p - W]) * 0.5f;
        gz[p * 2] = gx; gz[p * 2 + 1] = gy;
      }
    static const float hk[5] = {1.0f / 16, 1.0f / 4, 3.0f / 8, 1.0f / 4, 1.0f / 16};
    std::vector<float> bi(n * 3), bs(n * 3);
    for (int it = 0; it < ITERS; it++) {
      int step = 1 << it;
      float sl = 1.6f * powf(0.6f, (float)it);
#pragma omp parallel for schedule(dynamic, 16)
      for (int y = 0; y < H; y++)
        for (int x = 0; x < W; x++) {
          size_t p = (size_t)y * W + x;
          uint16_t ip = c.id[p] & 0x7FFF;
          const float* np_ = &c.nrm[p * 3];
          float zp = c.dep[p];
          float lp = lum3(&ai[p * 3]), lsp = lum3(&as[p * 3]);
          float sgl = std::max(sl / sqrtf(wi[p]), 0.07f) * (lp + 0.02f);
          float sgs = std::max(1.5f * sl / sqrtf(ws[p]), 0.10f) * (lsp + 0.02f);
          float si[3] = {0, 0, 0}, ss[3] = {0, 0, 0}, wsi = 0, wss = 0;
          float ri[3] = {0, 0, 0}, rs[3] = {0, 0, 0}, wri = 0;   // relaxed tier for orphan pixels (thin slivers)
          bool hasSpec = lsp > 0 || c.Ps[p] > 0;
          for (int dy = -2; dy <= 2; dy++) {
            int yy = y + dy * step; if (yy < 0 || yy >= H) continue;
            for (int dx = -2; dx <= 2; dx++) {
              int xx = x + dx * step; if (xx < 0 || xx >= W) continue;
              size_t q = (size_t)yy * W + xx;
              {
                float wr = hk[dx + 2] * hk[dy + 2] * expf(-fabsf(c.dep[q] - zp) / (0.03f * zp)) * ((c.id[q] & 0x7FFF) == ip ? 1.0f : 0.2f);
                ri[0] += wr * ai[q * 3]; ri[1] += wr * ai[q * 3 + 1]; ri[2] += wr * ai[q * 3 + 2];
                rs[0] += wr * as[q * 3]; rs[1] += wr * as[q * 3 + 1]; rs[2] += wr * as[q * 3 + 2]; wri += wr;
              }
              if ((c.id[q] & 0x7FFF) != ip) continue;
              const float* nq = &c.nrm[q * 3];
              float dn = np_[0] * nq[0] + np_[1] * nq[1] + np_[2] * nq[2];
              if (dn < 0.8f) continue;
              float d2 = dn * dn, d4 = d2 * d2, d8 = d4 * d4, wn = d8 * d8 * d8 * d8;
              float ez = fabsf(gz[p * 2] * (dx * step) + gz[p * 2 + 1] * (dy * step));
              float wz = expf(-fabsf(c.dep[q] - zp) / (1.5f * ez + 0.004f * zp + 1e-4f));
              float wg = hk[dx + 2] * hk[dy + 2] * wn * wz;
              if (wg < 1e-5f) continue;
              float lq = lum3(&ai[q * 3]);
              float w = wg * expf(-fabsf(lq - lp) / sgl);
              si[0] += w * ai[q * 3]; si[1] += w * ai[q * 3 + 1]; si[2] += w * ai[q * 3 + 2]; wsi += w;
              if (hasSpec) {
                float lq2 = lum3(&as[q * 3]);
                float w2 = wg * expf(-fabsf(lq2 - lsp) / sgs);
                ss[0] += w2 * as[q * 3]; ss[1] += w2 * as[q * 3 + 1]; ss[2] += w2 * as[q * 3 + 2]; wss += w2;
              }
            }
          }
          const float wc = hk[2] * hk[2];
          bool orphan = it < 2 && wsi < wc * 1.7f && wri > wc * 1.7f;
          if (orphan) { bi[p * 3] = ri[0] / wri; bi[p * 3 + 1] = ri[1] / wri; bi[p * 3 + 2] = ri[2] / wri; }
          else if (wsi > 0) { bi[p * 3] = si[0] / wsi; bi[p * 3 + 1] = si[1] / wsi; bi[p * 3 + 2] = si[2] / wsi; }
          else { bi[p * 3] = ai[p * 3]; bi[p * 3 + 1] = ai[p * 3 + 1]; bi[p * 3 + 2] = ai[p * 3 + 2]; }
          if (orphan && hasSpec) { bs[p * 3] = rs[0] / wri; bs[p * 3 + 1] = rs[1] / wri; bs[p * 3 + 2] = rs[2] / wri; }
          else if (wss > 0) { bs[p * 3] = ss[0] / wss; bs[p * 3 + 1] = ss[1] / wss; bs[p * 3 + 2] = ss[2] / wss; }
          else { bs[p * 3] = as[p * 3]; bs[p * 3 + 1] = as[p * 3 + 1]; bs[p * 3 + 2] = as[p * 3 + 2]; }
        }
      ai.swap(bi); as.swap(bs);
    }
    std::vector<uint16_t> out(n * 3);
#pragma omp parallel for schedule(static)
    for (long long p = 0; p < (long long)n * 3; p++) {
      float v = aa[p] * ai[p] + as[p] + ae[p];
      if (!(v == v)) v = 0;
      v = std::min(std::max(v, 0.0f), 60000.0f);
      out[p] = (uint16_t)_cvtss_sh(v, _MM_FROUND_TO_NEAREST_INT | _MM_FROUND_NO_EXC);
    }
    char name[512]; snprintf(name, sizeof(name), "%s_%04d.bin", outp.c_str(), pidx[i]);
    std::string tmp = std::string(name) + ".tmp";
    FILE* fo = fopen(tmp.c_str(), "wb");
    int hdr[2] = {W, H}; fwrite(hdr, 4, 2, fo); fwrite(out.data(), 2, out.size(), fo); fclose(fo);
    rename(tmp.c_str(), name);
    fprintf(stderr, "dn %d (rec %d) window %d..%d  %.1fs\n", i, pidx[i], lo, hi, omp_get_wtime() - t0);
  }
  return 0;
}
