/**
 * عقارAI — الخادم الخلفي الآمن (Cloudflare Worker)
 * -----------------------------------------------------------
 * وظيفة هذا الملف الوحيدة: استقبال سؤال المستخدم من الموقع، إرساله إلى Claude API
 * باستخدام مفتاح مخزَّن كسرّ على الخادم (Secret) لا يظهر أبداً في المتصفح، ثم إعادة الرد.
 *
 * لن يرى أي زائر لموقعك هذا المفتاح مهما فتح أدوات المطوّر أو راقب الشبكة،
 * لأن الطلب إلى Anthropic API يحدث بالكامل على خوادم Cloudflare لا في متصفح المستخدم.
 *
 * ===== خطوات النشر (مجاني بالكامل على Cloudflare) =====
 * 1) أنشئ حساباً مجانياً على https://dash.cloudflare.com
 * 2) ثبّت أداة wrangler محلياً:
 *      npm install -g wrangler
 * 3) سجّل الدخول:
 *      wrangler login
 * 4) في مجلد فيه هذا الملف و wrangler.toml المرفق، تأكد المحتوى مطابق لـ:
 *
 *      name = "aqarai-backend"
 *      main = "worker.js"
 *      compatibility_date = "2024-01-01"
 *
 * 5) أضف مفتاح Claude كسرّ (لن يظهر أبداً في الكود ولا في GitHub):
 *      wrangler secret put ANTHROPIC_API_KEY
 *    (سيطلب منك لصق المفتاح sk-ant-... ثم يحفظه بأمان على خوادم Cloudflare فقط)
 * 6) انشر:
 *      wrangler deploy
 * 7) سيعطيك رابطاً شبيهاً بـ:
 *      https://aqarai-backend.YOUR-SUBDOMAIN.workers.dev
 * 8) افتح index.html وضع هذا الرابط + "/chat" في متغيّر PROXY_URL أعلى قسم السكربت.
 *
 * ملاحظة أمان: ALLOWED_ORIGIN أدناه يقيّد من يستطيع استخدام الخادم بموقعك فقط.
 * تم تعيينه مسبقاً لدومين GitHub Pages الفعلي (ahmedvall70.github.io). لو غيّرت
 * دومين الموقع مستقبلاً (نطاق مخصص مثلاً)، حدّث القيمة أدناه وأعد النشر بأمر wrangler deploy.
 */

const ALLOWED_ORIGIN = "https://ahmedvall70.github.io"; // مقيّد لدومين GitHub Pages الفعلي لموقعك
const MODEL = "claude-sonnet-5";
const MAX_TOKENS = 1000;

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": ALLOWED_ORIGIN,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
  };
}

export default {
  async fetch(request, env) {
    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders() });
    }

    if (request.method !== "POST") {
      return new Response(JSON.stringify({ error: "Method not allowed" }), {
        status: 405,
        headers: { "Content-Type": "application/json", ...corsHeaders() },
      });
    }

    if (!env.ANTHROPIC_API_KEY) {
      return new Response(
        JSON.stringify({ error: "لم يتم ضبط مفتاح API على الخادم بعد. استخدم: wrangler secret put ANTHROPIC_API_KEY" }),
        { status: 500, headers: { "Content-Type": "application/json", ...corsHeaders() } }
      );
    }

    let body;
    try {
      body = await request.json();
    } catch (e) {
      return new Response(JSON.stringify({ error: "Invalid JSON body" }), {
        status: 400,
        headers: { "Content-Type": "application/json", ...corsHeaders() },
      });
    }

    // ملاحظة: الصيغة {system, messages} تطابق ما يرسله index.html في عقارAI
    // (خلافاً لنسخة قطر الأصلية التي كانت ترسل {message, language, history} غير المتوافقة مع هذا الخادم)
    const { system, messages } = body;

    if (!Array.isArray(messages) || messages.length === 0) {
      return new Response(JSON.stringify({ error: "messages is required" }), {
        status: 400,
        headers: { "Content-Type": "application/json", ...corsHeaders() },
      });
    }

    if (messages.length > 40) {
      return new Response(JSON.stringify({ error: "المحادثة طويلة جداً" }), {
        status: 400,
        headers: { "Content-Type": "application/json", ...corsHeaders() },
      });
    }

    try {
      const anthropicResponse = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-api-key": env.ANTHROPIC_API_KEY,
          "anthropic-version": "2023-06-01",
        },
        body: JSON.stringify({
          model: MODEL,
          max_tokens: MAX_TOKENS,
          system: system || "",
          messages,
        }),
      });

      if (!anthropicResponse.ok) {
        const errText = await anthropicResponse.text();
        return new Response(
          JSON.stringify({ error: `Anthropic API error: ${anthropicResponse.status}`, detail: errText }),
          { status: 502, headers: { "Content-Type": "application/json", ...corsHeaders() } }
        );
      }

      const data = await anthropicResponse.json();
      const reply = (data.content || [])
        .map((block) => (block.type === "text" ? block.text : ""))
        .join("");

      return new Response(JSON.stringify({ reply }), {
        status: 200,
        headers: { "Content-Type": "application/json", ...corsHeaders() },
      });
    } catch (err) {
      return new Response(JSON.stringify({ error: "Server error", detail: String(err) }), {
        status: 500,
        headers: { "Content-Type": "application/json", ...corsHeaders() },
      });
    }
  },
};
