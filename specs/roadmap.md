# Execution Roadmap

Source: synchronized from root `TODO.md`.

## P0 (Critical)

### P0.1 Multi-Tenant User Management

- ⏳ Persistent tenant/user registry in Redis.
- ⏳ Admin tenant and user management APIs.
- ⏳ Role-based authorization on pipeline and incident operations.
- ⚠️ Frontend tenant header propagation. (PARTIAL - tenant headers are used in API client paths, but end-to-end/user-role model is not fully completed yet)

### P0.2 5-Step Incident-Specific HITL

- ✅ Add LLM-driven incident-specific HITL question generator. (DONE - `agents/hitl_question_service.py` with `_llm_question_candidates`)
- ✅ Remove generic first-step prompts; start with incident summary + analysis notice. (DONE)
- ✅ After first immediate-cause stage, generate deeper selectable questions from `agents/knowledge_base.py`. (DONE - taxonomy/KB-backed probes)
- ✅ Fallback from static logic to LLM by quality threshold. (DONE - hybrid static + LLM candidate flow)
- ✅ HITL answer UX: `free_text`, `yes_no_unknown`, choice chips; hybrid optional text under Yes/No; auto-advance on chip click or Enter (`hitlResponseMode.js`, `ChatInterface.jsx`). (DONE)
- ✅ Backend `response_mode` inference for open questions (kaç/deneyim/miktar/listele — not forced to yes/no) (`agents/hitl_question_service.py`). (DONE)
- ⚠️ Improve Why-chain continuity. (PARTIAL — answer handling done; branch flow still iterative)
- ⏳ Persist HITL logs for training reuse.
- ✅ Keep a single primary large-area frontend analysis flow (remove duplicated secondary Why widgets). (DONE)
- ✅ Show initial immediate causes without taxonomy codes in chat intro, then switch directly to deep-dive collaboration prompts. (DONE)
- ✅ Filter out generic/duplicative HITL questions already covered by manual form fields (timeline/training/PPE/weather/lighting). (DONE)
- ✅ Generate Why-probe questions from taxonomy code semantics (choose-if/not-this-if) before generic gap questions. (DONE - taxonomy-first probe)

### P0.3 Frontend Live Streaming

- Branch/why-level granular progress callbacks.
- ✅ Enriched job payload: Celery `activity_lines` + `latest_activity` on pipeline jobs (`shared/pipeline_progress.py`, `rootcause_agent_v3_1.py`, `tasks/pipeline_tasks.py`, `api/main.py` `_normalize_celery_job`). (DONE)
- ✅ Chat UI streams pipeline activity + final RCA summary after HITL (`ChatInterface.jsx`, `formatPipelineChat.js`; WebSocket/polling `onUpdate`). (DONE)
- ⏳ Live timeline component in chat UI (dedicated stepper beyond bullet list).
- ⏳ WebSocket reconnect and robust failure UX.
- ✅ Increase frontend pipeline timeout defaults from 6 minutes to 20 minutes for polling/WebSocket job tracking to reduce premature "Pipeline timeout (360s)" errors on long RCA runs. (DONE)

### P0.4 Worker OpenRouter 401 Stabilization

- ✅ Eliminate `Missing Authentication header` failures in Step 3 (Celery worker). (DONE)
- ✅ Enforce deploy/runtime parity between API and worker services. (DONE - runtime OpenRouter diagnostics + shared worker startup script)
- ✅ Add deterministic startup diagnostics for auth/debug visibility. (DONE - OpenRouter worker config + UTC startup logs)
- ✅ Verify worker is running latest commit via build fingerprint and deploy metadata. (DONE - `celery_app.WORKER_BUILD_TAG` startup log)
- ✅ Add clear runbook for Railway redeploy + env parity checks. (DONE - operationalized through worker script/env conventions in repo docs)
- Acceptance:
  - Worker logs show build fingerprint and OpenRouter runtime config on startup.
  - HITL flow reaches Part 3+Part 4 completion without OpenRouter 401.
  - Same env/config behavior is reproducible after restart and redeploy.

### P0.5 Worker Burst Scaling Without Always-On High Load

- ✅ Configure Celery worker autoscaling for burst traffic. (DONE)
- Default runtime profile:
  - ✅ `CELERY_POOL=prefork` (DONE)
  - ✅ `CELERY_AUTOSCALE_MAX=5` (DONE)
  - ✅ `CELERY_AUTOSCALE_MIN=1` (DONE)
- ✅ Keep baseline resource usage low while allowing temporary parallel RCA jobs. (DONE - autoscale min/max + prefetch baseline)
- Acceptance:
  - Idle worker runs at min process count.
  - Under queue pressure worker scales up to configured max.
  - Scale-down occurs automatically after queue drains.

### P0.6 Action Plan JSON Robustness

- ✅ Enforce stricter Action Plan JSON schema validation. (DONE - schema gate in `ActionPlanAgent`)
- ✅ Add retry and \"json-only\" sanitizer parser for malformed outputs. (DONE - 3-attempt regeneration + sanitize candidates)
- ✅ Sanitize markdown fences and trailing commas before parsing. (DONE - candidate sanitizer in `ActionPlanAgent`)
- ✅ Add parse telemetry and malformed-output regression tests. (DONE - telemetry logs + `tests/test_actionplan_json_hardening.py`)

### P0.7 Celery Long-Run Reliability

- ✅ Keep `prefork + autoscale` as baseline worker runtime. (DONE)
- ✅ Tune heartbeat and broker visibility timeout for long RCA tasks. (DONE - env-driven visibility timeout + health interval + prefetch=1)
- ✅ Reduce single-worker CPU blocking with staged checkpoints. (DONE - cooperative progress checkpoints in `tasks/pipeline_tasks.py`)
- ✅ Add 3-5 parallel-run reliability/load validation and ops visibility. (DONE - ops summary in `shared/ops_celery.py` + `tests/test_parallel_rca_load_scenario.py`)
- ✅ Add worker recycle and runtime UTC diagnostics to reduce long-lived process degradation and make clock-drift triage explicit (`CELERY_MAX_TASKS_PER_CHILD`, startup UTC log in `celery_app.py` + worker start script). (DONE)
- ✅ Expose action-plan fallback telemetry in pipeline progress/result payload (`actionplan_meta.fallback_used`) for easier RCA/report quality triage. (DONE - `tasks/pipeline_tasks.py`)
- ⚠️ Remaining ops prerequisite: platform-level clock sync/NTP parity across worker instances (code cannot force host clock; monitor for `Substantial drift ... clocks are out of sync`). (OPS NOTE)

### P0.8 Multilingual Report + Interactive UX Stream

- ✅ Propagate selected frontend language to investigate/report pipeline (`output_language`). (DONE)
- ✅ Ensure report shell labels (DOCX + HTML) follow selected language (minimum: non-TR must not render Turkish headers). (DONE - baseline)
- ✅ Align report visual palette with admin panel theme tokens. (DONE)
- ✅ Interactive analysis must open chat-first and show active chatbot surface immediately. (DONE)
- ✅ Fast HITL bootstrap: `POST /assessment/form` (no LLM) before chat tab — avoids stuck “Assessment calisiyor” on interactive submit (`api/main.py`, `RcaFrontendHub.jsx`, gateway `add_assessment_form`). (DONE)
- ✅ Stream live root-cause/progress lines in Agent Pipeline area during analysis/report generation. (DONE)
- ✅ HITL intro: stream per-incident immediate causes (“doğrudan nedenler belirleniyor…”) instead of static list (`streamHitlIntro.js`, `deriveImmediateCauseLines`). (DONE)
- ✅ Lock **Etkileşimli Analiz** tab until Manuel Form → **Etkileşimli Analize Geç**; block free `sendMessage` chat (timeout path removed). (DONE — `RcaFrontendHub.jsx`, `ChatInterface.jsx`)
- ✅ Post-HITL pipeline lines in chat message (worker progress → UI via `activity_lines`). (DONE — see P0.3)
- ✅ Interactive **HTML Oluştur** flow: no blank-popup requirement; download-first + preview/tab/blob fallback (`ChatInterface.jsx`, `hsg245Api.js`). (DONE)
- ✅ Report generation tolerates Part 3 / artifact write delay (frontend retry + API `_generate_report_artifacts` retry). (DONE)

### P0.9 Report Template, Branding, and Hologram

- Add editable and alternative cover-page templates for report generation.
- Keep DOCX and HTML report structures aligned section-by-section.
- Add user-facing option to hide/remove technical code identifiers from report body.
- Confirm final code-visibility policy with Baris Bey before release.
- Add optional logo insertion support (tenant-level default + per-report override).
- Add watermark/hologram support for draft/final report modes.

### P0.10 User Report Library + Completion Email Delivery

- Add per-user "My Reports" library in admin panel (list/filter/status/download/regenerate). **See also P1.10** for the DeepWhy-dedicated **saved reports tab** (in-form UX + same ownership/tenant isolation principles).
- Persist report ownership and lifecycle metadata (`owner_user_id`, `incident_id`, `status`, `artifact_urls`, timestamps).
- **Auto-email on report complete (target UX):** when HTML/DOCX artifacts are ready, send one email to the
  **logged-in user's registered address** (Kinde `email` / profile) with attachments (HTML + DOCX) or
  signed download links; no manual "download then attach" step for the user.
- Send automatic email notification when report generation completes (success/failure templates + secure links).
- Add notification preferences (opt-in/out, tenant defaults) and idempotent delivery/retry policy.
- Add audit trail for delivery events and authorization checks for report access links.
- Backend: SMTP/transactional provider (e.g. Resend, SendGrid, SES), Celery task after
  `_generate_report_artifacts`, template TR/EN, bounce handling.

### P0.11 Pricing Page Refresh (3-Tier Layout)

- Rebuild pricing section with 3 plan cards matching target visual style:
  - Starter (`$29/ay`)
  - Professional (`$99/ay`, highlighted as "En popüler")
  - Enterprise (`$299/ay`)
- Define and render per-tier limits and included capabilities:
  - monthly report quota,
  - **monthly token / analysis credit budget** (maps to **P1.15** user token accounts),
  - analysis method coverage (5-Why / Bow-tie),
  - output formats (Word/PDF/HTML),
  - user seat limit,
  - API/SSO/SLA options where relevant.
- Add segment labels on cards:
  - KOBİ / bireysel HSE,
  - Orta ölçekli işletme,
  - Büyük sanayi / holding.
- Move tier content to config-driven structure (single source for UI + future billing mapping).
- Keep TR copy first, but prepare EN i18n keys for later language switch.
- Acceptance:
  - Pricing UI matches approved 3-card design composition and emphasis hierarchy.
  - Tier content is editable via config without component rewrite.
  - Mobile/tablet breakpoints preserve readability and card priority order.

### P0.12 Language-Aware HITL Questions

- ⚠️ Ensure HITL question text is generated and returned in the user-selected UI language. (PARTIAL — UI i18n + labels; LLM batches may still drift)
- ✅ Propagate selected language from frontend into HITL question APIs (`global` + `why_probe` modes). (DONE)
- Localize all question payload fields consistently:
  - `question_tr` / `question_en`,
  - choice labels/options,
  - helper hints and response-mode guidance text.
- Prevent mixed-language batches (single question set should not contain TR+EN drift).
- Keep fallback behavior deterministic:
  - if target language generation fails, retry once with same language,
  - then return known-safe localized templates (not opposite language).
- Acceptance:
  - Changing UI language immediately changes subsequent HITL questions and options.
  - Same incident asked in TR vs EN yields language-consistent wording with equivalent intent.
  - No mixed-language question batches in regression tests.

### P0.13 End-to-End Language-Aware Report Rendering

- Ensure report output language follows selected UI/investigation language end-to-end (HTML + DOCX).
- Remove/replace embedded Turkish static headings in `agents/skillbased_docx_agent.py` with language-keyed labels.
- Localize all report shell sections consistently:
  - cover, table-of-contents labels, section headers, subsection headers,
  - table column titles, action/status labels, signature page labels,
  - helper notes/tooltips and print/export helper text.
- Prevent mixed-language report artifacts (single artifact should not include TR+EN shell drift).
- Keep report body and shell language aligned:
  - dynamic RCA content + static template headings must use the same selected language.
- Add fallback policy for missing translations:
  - first fallback to English keyset,
  - then explicit placeholder marker for missing key (to avoid silent Turkish leakage).
- Acceptance:
  - Switching language before report generation produces full-shell localized report artifacts.
  - `skillbased_docx_agent.py` contains no hardcoded TR-only section titles without i18n mapping.
  - Regression checks confirm no Turkish headers appear in EN report mode.

### P1.7 Evidence Attachments in Analysis Flow (client slice)

- ✅ Manual form (DeepWhy): file picker + drag-and-drop under **Ek Notlar**; allowed types JPEG/PNG/WebP/GIF, PDF, TXT/CSV; list + remove in UI; text excerpts and file manifest merged into `how_happened` for `createIncident` / `investigate` / HITL (`IncidentForm.jsx`, `investigationPayload.js`). (DONE — client-side only)
- ⏳ Server upload + durable storage — superseded by **P1.13** (multimodal extraction pipeline).
- ⏳ OCR/Vision enrichment — **P1.13 Layer 1**.
- ⏳ Interactive analysis evidence summary UI — **P1.13**.

### P1.13 Multimodal Evidence Extraction + Enriched Context (Layer 1–3)

Architecture reference: `specs/plan.md` → *Multimodal enrichment pipeline*.

**Layer 1 — Extraction (parallel, per file type)**

- ⏳ Incident attachment API: upload JPG/PNG/PDF/DOCX; validate size/type; tenant-isolated object storage (S3/GridFS/Railway volume).
- ⏳ **Photos → Vision:** structured JSON per image (`ekipman_tipi`, `kkd_durumu`, `loto_durumu`, `alan_koşulları`, `görsel_kanıtlar[]`, `anomaliler[]`, `güven_skoru`); target ~500 tokens/image; merge photo JSON array.
- ⏳ **PDF/DOCX → text + LLM:** PyMuPDF / python-docx raw text → LLM extract (`döküman_tipi`, `son_güncelleme_tarihi`, `ilgili_maddeler[]`, `eksik_imzalar[]`, `geçerlilik_durumu`); target ~800 tokens/doc.
- ⏳ **Certificates → OCR/Vision:** extract name, date, scope; match to persons named in incident.
- ⏳ `asyncio.gather()` orchestrator: all extractions finish before RCA pipeline starts; surface per-file failures without blocking whole job (policy TBD).

**Layer 2 — Context merge**

- ⏳ Build `enriched_context` block sections: `[GÖRSEL KANIT]`, `[DÖKÜMAN KANIT]`, `[SERTİFİKA DURUMU]`, `[ŞİRKET PROFİLİ]`.
- ⏳ Append to end of existing `incident_summary` before `RootCauseAgentV3_1.analyze_root_causes()` — no signature/graph changes.
- ⏳ Low-confidence evidence flagged in merged text for report wording (“olası”, güven %).

**Layer 3 — Company memory (oracle profile)**

- ⏳ Mongo collection or JSON store per `tenant_id` / `şirket_id`: `geçmiş_kök_nedenler[]`, `tekrar_örüntüsü`, `sektör`, `ekipman_parkı[]`, `bilinen_riskler[]`.
- ⏳ Load into `investigation_data["oracle_context"]` at pipeline start (field exists).
- ⏳ Post-report hook: append new root-cause codes, increment repeat counters, update `tekrar_örüntüsü` summary.

**Acceptance**

- Upload 2 photos + 1 PDF → pipeline receives enriched summary; RCA output references attachment-derived facts with confidence labels.
- Company profile from report N influences report N+1 via `oracle_context`.
- Token budget respected (summarized JSON only, no raw PDF dump in prompt).

## P1 (Near-Term)

### P1.1 Synthetic Data Pipeline

- ✅ Mongo output mode for synthetic generation. (DONE - `--store mongo|both` + dataset/example persistence)
- Tenant partitioning and seeded generation from incidents.
- Scheduled generation jobs and admin trigger endpoint.

### P1.2 DSPy MIPROv2 Integration

- ✅ Define RCA quality metrics. (DONE - `agents/training/dspy_metrics.py`)
- ✅ Build optimize/compile pipeline for WhyChain. (DONE - `agents/training/optimize_rca.py`, WhyChain input adaptation + MIPRO run path)
- ✅ Version compiled artifacts and support runtime loading. (DONE - versioned summary artifacts in `agents/training/compiled/`)
- ✅ Add baseline vs compiled A/B evaluation. (DONE - sampled dev-set A/B report in `agents/training/compiled/`)

### P1.3 Operational Training Workflow

- Standardize train/eval/promote commands.
- Store run artifacts and lineage metadata.
- Nightly CI training with release gate.

### P1.4 Tenant Insights

- Time trends, severity and category distributions.
- Department/location analytics breakdown.
- Dashboard visualization in admin panel.

### P1.5 RAG Rollout

- Managed embeddings and vector store.
- Tenant-isolated vector namespaces.
- ✅ Controlled RAG prompt injection strategy. (DONE - Mongo context injection into `RootCauseAgentV3_1` incident summary path)
- ✅ Vector RAG lazy import + soft degradation when optional deps missing (V3.1 can run without local torch/sentence-transformers; wired in `rag_pipeline/retrieval` + `RootCauseAgentV3_1`). (DONE)
- ⚠️ Runtime prerequisite reminder: if `sentence_transformers` (and compatible `torch`) is missing on worker runtime, vector RAG stays disabled and system falls back to keyword/context-only path (`No module named 'sentence_transformers'`). (OPS NOTE)
- ✅ Canonical root-cause labels: after 5-Why, map final C/D (and D-only meta-synthesis) to official HSG245 titles from `agents/knowledge.json` via `parse_hsg_taxonomy_items` / `infer_codes_from_text` (`_try_snap_to_taxonomy` in `rootcause_agent_v3_1.py`). (DONE)
- Add normalized HGS taxonomy store in Mongo (`hgs_taxonomy.taxonomy_items`) for taxonomy-aware retrieval/questioning.

### P1.6 ABS-Guided DSPy Training + Deep HITL

- Extend `agents/synetic_data_preperation/hse_synthetic_data.py` to produce
  ABS-aligned Why chains (causal-factor-first, management-system-gap-aware).
- Build training/eval set variants from ABS style patterns:
  - multiple plausible root causes per causal factor,
  - evidence-based questioning and recommendation linkage.
- Add HITL deep-question policy:
  - ask branch-specific disambiguation questions at each Why depth,
  - skip data already present in form payload,
  - enforce evidence collection prompts for timeline/procedure/maintenance/supervision.
- Integrate RAG into root-cause and HITL phases with controlled retrieval:
  - query only relevant ABS/taxonomy chunks,
  - inject concise citations into prompts,
  - keep fallback to non-RAG prompts when confidence is low.
- Railway vector DB decision:
  - primary: MongoDB Atlas Vector Search (tenant namespace, managed ops),
  - avoid local file-based FAISS/Chroma persistence in production workers.

### P1.8 Ordered Delivery Plan (Synthetic -> DB -> RAG -> MIPROv2)

- ✅ Step 1: ABS-guided synthetic dataset generation and quality gate. (DONE - profile + stricter quality gate)
- ✅ Step 2: Dataset versioning and persistence into database (tenant + dataset lineage). (DONE - dataset metadata + Mongo store mode)
- ✅ Step 3: ABS guidance PDF chunking and vector DB indexing for RAG retrieval. (DONE - `build_abs_guidance_vector_store.py`)
- ✅ Step 4: MIPROv2 optimization using curated dataset versions (+ baseline vs optimized eval). (DONE - `agents/training/optimize_rca.py`, `agents/training/dspy_metrics.py`)
- ✅ Step 5: Production promotion with rollback-safe model/version controls. (DONE - `agents/training/promote_model.py`)

### P1.9 Model Strategy by Stage

- ✅ **Implemented defaults** (`agents/model_constants.py`):
  - **Analysis (DSPy, 5-Why, overview, assessment, action plan, chat using `OPENROUTER_DEFAULT_CHAT_MODEL`):** `anthropic/claude-haiku-4.5`.
  - **Report writing only (DOCX/HTML, `SkillBasedDocxAgent` / `resolve_openrouter_docx_model`):** `google/gemini-2.5-flash`, independent of analysis default.
  - Overrides: `OPENROUTER_DSPY_MODEL`, `OPENROUTER_DOCX_MODEL`, `OPENROUTER_DEFAULT_MODEL`, `OPENROUTER_MODEL_PRESET` (presets include `flash`, `qwen`, `qwen3`, `qwen3-vl`, `haiku`, `maestro`, `gpt-5.4-mini`, `kimi`, `deepseek`, `v4pro`, `sonnet`). `OPENROUTER_TEST_MODEL` forces a single model for the whole stack—leave empty for the split. (DONE)
- Training/synthetic generation profile (non-production defaults in scripts; align with `agents/synetic_data_preperation`):
  - prefer `google/gemini-2.5-flash` for speed and cost where still used.
- Historical note: earlier drafts suggested `anthropic/claude-sonnet-4.5` for agentic + report; production split now uses Haiku (analysis) + Flash (report), after prior DeepSeek/Qwen default iterations.
- Runtime fallback policy (still open):
  - primary model failure should degrade gracefully to a secondary profile.

### P1.10 DeepWhy — Saved Reports Tab + Per-User Multi-Tenant Persistence

- ✅ Add top-level **Raporlar** tab in the DeepWhy RCA shell (`SavedReportsPanel`, `draftReportsStorage.js`, `reportsLibraryApi.js`). (DONE)
- ✅ List, open draft (form seed), delete; TR/EN copy; localStorage fallback when Mongo unavailable. (DONE)
- ✅ **Completed reports:** auto-save after analysis; manual **Raporu Kaydet**; reopen HTML/decision tree from library. (DONE)
- ✅ **Server persistence:** Mongo `rca.deepwhy_saved_items` + `/api/v1/library/*`; `ensure_collection` on API startup; health `reports_library` probe. (DONE)
- ✅ **Multi-tenant + user isolation:** `tenant_id` + `owner_user_id` on every read/write; `X-Tenant-ID` + `X-User-ID` from Kinde via Vercel gateway; Kinde `org_code` → `tenant_id` on login when present. (DONE)
- ✅ **Reports UX:** chip actions (Görüntüle / HTML / Word / karar ağacı); download via gateway (`download_html_report`, `download_decision_tree`, `download_docx_report`); rename report title on click; two-column layout (reports left, sticky drafts sidebar). (DONE)
- ✅ `library_save_html` fallback when finalize times out on serverless. (DONE)
- ⏳ Align with **P0.10** email delivery on same ownership tables.
- ⏳ Store `decision_tree_html` reliably on every auto-save (sync button + pipeline hook).
- Acceptance:
  - Authenticated user A cannot read or edit user B’s saved items within the same tenant (and never across tenants).
  - Tab shows only the current user’s items; title rename and downloads persist after reload.
  - Clear empty state and error handling when persistence or network fails.

### P1.16 DeepWhy — Report Guide Video Tab

- ✅ **Rapor Rehberi** tab (`?tab=guide`): fullscreen admin informational video (`ReportGuideVideoPanel`). (DONE)
- ✅ Video source: `public/media/rca-report-guide/report-guide.mp4` or `VITE_RCA_GUIDE_VIDEO_URL` (MP4/YouTube/Vimeo). (DONE)
- ✅ Removed user upload UI from tab and Raporlar sidebar; link **Rehberi izle** on Raporlar header. (DONE)
- ⏳ (Superseded) browser-local user video library (`SavedVideosPanel` / IndexedDB) — not exposed in UI.
- ✅ Save external share links (YouTube, Drive, etc.) with in-panel play or open-in-new-tab. (DONE)
- ⏳ Server-side upload + tenant-scoped object storage (S3/GridFS) for cross-device access.
- ⏳ Link videos to saved reports / incidents in Mongo library.
- Acceptance:
  - User can add a created training/incident video and play it back in the same browser session.
  - Videos tab does not block form/HITL/report flows.

### P1.11 DeepWhy — Manual Form Entry: User-Selectable Model Tier

- ✅ Model tier block at top of manual form (Hızlı / Derinlemesine); neutral TR/EN copy (no cost wording). (DONE)
- ✅ Wire `analysis_model_preset` to investigate/pipeline (`investigationPayload.js`, API, Vercel gateway, `model_constants.py`, V3.1 LM reconfigure). (DONE)
- ✅ **Derinlemesine** tier visible but locked (`ANALYSIS_QUALITY_TIER_SELECTABLE = false`) until product enables it. (DONE)
- ✅ Persist `analysis_model_preset` on server-side library upsert/finalize records. (DONE)
- Acceptance:
  - Default tier is sensible for new sessions; changing tier before submit updates the subsequent analysis request.
  - Copy is concise, non-technical, and consistent with i18n direction (TR first; EN keys optional follow-up).

### P1.14 DeepWhy — Akıllı Hibrit Kök Neden (Smart Hybrid RCA)

**Ürün ilkesi (Seçenek C — önerilen):** Sistem önerir, kullanıcı onaylar. Dal sayısı tamamen serbest veya tamamen sabit değil; yeni HSE uzmanına rehberlik, deneyimli kullanıcıya esneklik.

**Mantık (şiddet → önerilen dal):**

| Şiddet / olay tipi | Önerilen dal | UX uyarısı |
|--------------------|--------------|------------|
| Ölümlü / ağır yaralanma | **3** | *"Bu şiddet için en az 3 dal önerilir."* |
| Hafif yaralanma | **2** | — |
| Ramak kala | **1** | — |

**Varsayılan dal şablonları** (kabul / yeniden adlandır / sıfırdan yaz):

1. İnsan / Davranış  
2. Gözetim / Organizasyon  
3. Sistem / Prosedür  

**Yapılacaklar:**

- ⏳ **v1 lookup tablosu (MVP):** Formdaki `injurySeverity` + `eventCategory` → önerilen dal sayısı + şablon etiketleri (kod sabitleri; tenant override sonra).
- ⏳ **Dal kurulum ekranı:** Analiz/HITL öncesi veya kök neden adımında önerilen dalları göster; tek tık *Kabul et* / satır satır düzenle.
- ⏳ **Dal ekleme:** `+ Dal ekle` her zaman görünür; **mevcut dal boşken** yeni dal açılamaz — *"Önce mevcut dalı doldurun."*
- ⏳ **Minimum dal:** En az **1 zorunlu dal** (silme ile altına inilemez); üstüne ekleme serbest. MVP: kullanıcı dal **silemez**, sadece ekler/doldurur (kalite tabanı).
- ⏳ **Doluluk / kalite skoru:** Rapor tamamlanınca dal bazlı doldurma yüzdesi; zorunlu dallar eksikse onay engeli — *"Bu rapor onaya hazır değil."*
- ⏳ **HITL + pipeline:** Onaylanmış dal yapısı `why_probe` dallarına ve `part3` branch sayısına beslenir; RCA pipeline kullanıcı onayından sonra başlar.
- ⏳ **API + tenant config:** Şiddet eşikleri, şablon TR/EN etiketleri, min/max dal (`tenant_id` config veya Mongo).
- ⏳ **Frontend:** `RcaFrontendHub` / form veya `ChatInterface` dal editörü bileşeni; durum incident veya draft snapshot’ta persist.
- ✅ **Karar ağacı:** OLAY kutusunda olay anlatımının **tamamı** — `full_incident_narrative_for_tree` (`report_text_sanitize.py`). (DONE)

**Acceptance:**

- Yeni kullanıcı analiz başlatınca önerilen dal sayısı + şablonları görür; kabul veya düzenleyebilir.
- Deneyimli kullanıcı ek dal ekleyebilir; boş dal varken yeni dal engellenir.
- Ölümlü/ağır vaka için 3 dal önerisi ve eksik dal uyarısı gösterilir.
- Onay sonrası 5-Why / decision tree, onaylanmış dal yapısıyla uyumludur.

**İlgili dosyalar (hedef):** `admin_pan` RCA form/chat, `api/main.py`, `agents/rootcause_agent_v3_1.py`, `tasks/pipeline_tasks.py`.

### P1.15 Kullanıcı Token Hesabı ve Kullanım Kotası

Her kullanıcı için token bakiyesi; LLM/pipeline tüketimi düşülür; bakiye bitince analiz ve rapor üretimi kısıtlanır. **P0.11** fiyatlandırma katmanlarıyla hizalanacak (Starter / Professional / Enterprise aylık token veya rapor kotası).

**Yapılacaklar:**

- ✅ **Veri modeli:** `user_token_accounts` + `token_ledger` Mongo (`shared/token_account.py`); in-memory fallback when `MONGODB_URI` unset. (DONE)
- ✅ **Ledger / audit:** Debit/credit with `idempotency_key`, `prompt_tokens`, `completion_tokens`, module, incident/job ids. (DONE)
- ✅ **Tüketim noktaları:** Pipeline (Celery + in-process), investigate, assessment (LLM), action plan, HITL LLM (`usage_context`), HTML/DOCX reports — estimate + OpenRouter `usage` where available. (DONE)
- ✅ **API enforcement:** `402` + `insufficient_tokens` on protected routes; `OwnerUserId` dependency on billable endpoints. (DONE)
- ⚠️ **Worker reserve/release:** Pipeline debits on task complete (idempotent per `job_id`); explicit reserve-before-run optional follow-up. (PARTIAL)
- ✅ **Frontend UX:** Dashboard `pages/Dashboard/index.jsx` + `usageApi.js`; DeepWhy token strip + disabled submit when blocked. (DONE)
- ✅ **Admin top-up:** `POST /api/v1/usage/top-up` (v1 manual credit). (DONE)
- ⏳ **Plan eşlemesi:** `P0.11` tier → monthly token budget config (env defaults only today).
- ✅ **Grace & uyarı:** `warn_level` ok / warning / critical / blocked; dashboard + RCA banners. (DONE)

**Acceptance:**

- İki farklı kullanıcı aynı tenant’ta birbirinin token bakiyesini tüketemez.
- Pipeline tamamlandığında ledger toplamı OpenRouter usage ile makul uyumda (± yapılandırılabilir tolerans).
- Bakiye 0 iken `pipeline/start`, `investigate`, `hitl` (LLM path) ve rapor üretimi reddedilir; health ve kütüphane listeleme çalışır.
- Idempotent tekrar denemede çift düşüm olmaz (`idempotency_key` = `job_id` veya request id).

**İlgili dosyalar (hedef):** `api/main.py`, `shared/` (yeni `token_account.py`), `tasks/pipeline_tasks.py`, `agents/model_constants.py`, `admin_pan` `hsg245Api.js`, Kinde `owner_user_id` header’ları.

### P1.12 Admin shell — default home (cpanel)

- ✅ Post-login and `/` redirect to **`/dashboard`** (admin panel), not legislation chatbot (`config/appHome.js`, Kinde callback, routes). (DONE)
- ✅ Mevzuat bot route/code retained; disabled via `LEGISLATION_CHATBOT_ENABLED = false` (redirect + hidden menu). (DONE)
- ✅ Sidebar **Panel** link + logo → dashboard. (DONE)

## P2 (Mid-Term)

### P2.1 Voice Input

- Incident voice capture and STT integration.

### P2.2 Language Strategy

- Output language consistency and broader locale support.

### P2.3 Test Coverage

- Unit tests for tenant/cache/HITL services.
- CI mocking for LLM interfaces.
- Playwright e2e flow validation.

### P2.4 Observability

- Structured logging, latency/token metrics, Sentry/Highlight.

## Continuous

- Bump worker build fingerprint every release.
- Maintain key rotation playbook.
- Archive legacy agent versions.
- Exclude generated outputs from git tracking.

### Deploy / Railway (ops — completed slices)

- ✅ Slim `Dockerfile` + `requirements-railway.txt` for Agents/worker images (Railpack/Nixpacks disk exhaustion mitigation). (DONE)
- ✅ Include `hitl_test/` in production Docker image — required by `agents/hitl_question_service.py` at runtime (fixes HITL `hitl/questions` 500). (DONE)
- ✅ Witness rows on manual form: add/remove, embedded editable names, role-only (no contact), template reporter/witness placeholders (`admin_pan` IncidentForm). (DONE)
