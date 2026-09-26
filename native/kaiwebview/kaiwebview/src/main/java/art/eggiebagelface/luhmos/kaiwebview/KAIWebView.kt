package art.eggiebagelface.luhmos.kaiwebview

import android.graphics.Color
import android.net.Uri
import android.os.Build
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.webkit.CookieManager
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.FrameLayout
import androidx.webkit.JavaScriptReplyProxy
import androidx.webkit.WebMessageCompat
import androidx.webkit.WebViewAssetLoader
import androidx.webkit.WebViewCompat
import androidx.webkit.WebViewFeature
import org.godotengine.godot.Godot
import org.godotengine.godot.plugin.GodotPlugin
import org.godotengine.godot.plugin.SignalInfo
import org.godotengine.godot.plugin.UsedByGodot
import org.json.JSONObject
import kotlin.math.min
import kotlin.math.roundToInt

class KAIWebView(godot: Godot) : GodotPlugin(godot) {
    companion object {
        private const val ORIGIN = "https://appassets.androidplatform.net"
        private const val START_URL = "$ORIGIN/assets/cockpit/index.html"
        private val BRIDGE_SIGNAL = SignalInfo("bridge_message", String::class.java)
        private val MODES = setOf("bubble", "compact", "panel", "fullscreen", "hidden")
    }

    private var webView: WebView? = null
    private var currentMode = "compact"

    override fun getPluginName() = BuildConfig.GODOT_PLUGIN_NAME
    override fun getPluginSignals() = setOf(BRIDGE_SIGNAL)

    @UsedByGodot
    fun showCockpit() {
        runOnHostThread {
            val view = ensureWebView()
            view.visibility = View.VISIBLE
            applyMode(currentMode)
        }
    }

    @UsedByGodot
    fun hideCockpit() {
        runOnHostThread { webView?.visibility = View.GONE }
    }

    @UsedByGodot
    fun setCockpitMode(mode: String) {
        if (mode !in MODES) return
        runOnHostThread { applyMode(mode) }
    }

    @UsedByGodot
    fun isCockpitReady(): Boolean = webView != null

    @UsedByGodot
    fun postToCockpit(json: String) {
        runOnHostThread {
            val quoted = JSONObject.quote(json)
            webView?.evaluateJavascript(
                "window.dispatchEvent(new MessageEvent('message',{data:$quoted}));",
                null
            )
        }
    }

    private fun dp(value: Int): Int {
        val host = activity ?: return value
        return (value * host.resources.displayMetrics.density).roundToInt()
    }

    private fun applyMode(mode: String) {
        val host = activity ?: return
        val view = ensureWebView()
        currentMode = mode
        if (mode == "hidden") {
            view.visibility = View.GONE
            return
        }
        view.visibility = View.VISIBLE
        val metrics = host.resources.displayMetrics
        val screenW = metrics.widthPixels
        val screenH = metrics.heightPixels
        val params = when (mode) {
            "bubble" -> FrameLayout.LayoutParams(dp(86), dp(86), Gravity.END or Gravity.BOTTOM).apply {
                rightMargin = dp(14); bottomMargin = dp(18)
            }
            "compact" -> FrameLayout.LayoutParams(min(screenW - dp(16), dp(430)), min(screenH - dp(28), dp(300)), Gravity.END or Gravity.BOTTOM).apply {
                rightMargin = dp(8); bottomMargin = dp(12)
            }
            "panel" -> FrameLayout.LayoutParams(screenW - dp(16), min(screenH - dp(24), (screenH * 0.62f).roundToInt()), Gravity.CENTER_HORIZONTAL or Gravity.BOTTOM).apply {
                leftMargin = dp(8); rightMargin = dp(8); bottomMargin = dp(10)
            }
            else -> FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT, Gravity.FILL)
        }
        view.layoutParams = params
        val quoted = JSONObject.quote(mode)
        view.evaluateJavascript("window.LuHmUISetMode&&window.LuHmUISetMode($quoted);", null)
    }

    private fun ensureWebView(): WebView {
        webView?.let { return it }
        val host = activity ?: error("KAIWebView host activity unavailable")
        val loader = WebViewAssetLoader.Builder()
            .addPathHandler("/assets/", WebViewAssetLoader.AssetsPathHandler(host))
            .build()

        WebView.setWebContentsDebuggingEnabled(false)
        val view = WebView(host)
        view.setBackgroundColor(Color.TRANSPARENT)
        view.overScrollMode = View.OVER_SCROLL_NEVER
        view.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = false
            allowFileAccess = false
            allowContentAccess = false
            mixedContentMode = WebSettings.MIXED_CONTENT_NEVER_ALLOW
            cacheMode = WebSettings.LOAD_NO_CACHE
            blockNetworkLoads = true
            mediaPlaybackRequiresUserGesture = true
            setSupportMultipleWindows(false)
            javaScriptCanOpenWindowsAutomatically = false
            saveFormData = false
        }
        CookieManager.getInstance().apply {
            setAcceptCookie(false)
            setAcceptThirdPartyCookies(view, false)
        }

        view.webViewClient = object : WebViewClient() {
            override fun shouldInterceptRequest(view: WebView?, request: WebResourceRequest?): WebResourceResponse? =
                request?.url?.let(loader::shouldInterceptRequest)

            override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
                val uri = request?.url ?: return true
                return uri.scheme != "https" || uri.host != "appassets.androidplatform.net"
            }
        }

        if (WebViewFeature.isFeatureSupported(WebViewFeature.WEB_MESSAGE_LISTENER)) {
            WebViewCompat.addWebMessageListener(
                view,
                "LuHmNative",
                setOf(ORIGIN),
                WebViewCompat.WebMessageListener { _, message, sourceOrigin, isMainFrame, replyProxy ->
                    handleBridgeMessage(message, sourceOrigin, isMainFrame, replyProxy)
                }
            )
        }

        val root = host.findViewById<ViewGroup>(android.R.id.content)
        root.addView(view, FrameLayout.LayoutParams(dp(430), dp(300), Gravity.END or Gravity.BOTTOM))
        view.loadUrl(START_URL)
        webView = view
        return view
    }

    private fun handleBridgeMessage(
        message: WebMessageCompat,
        sourceOrigin: Uri,
        isMainFrame: Boolean,
        replyProxy: JavaScriptReplyProxy
    ) {
        if (!isMainFrame || sourceOrigin.toString() != ORIGIN) return
        val raw = message.data ?: return
        val parsed = runCatching { JSONObject(raw) }.getOrNull() ?: return
        if (parsed.optString("schema") != "luhm.bridge.v1") return
        val type = parsed.optString("type")

        when (type) {
            "status.request" -> {
                val pkg = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) WebView.getCurrentWebViewPackage() else null
                replyProxy.postMessage(
                    JSONObject()
                        .put("schema", "luhm.bridge.reply.v1")
                        .put("type", "status")
                        .put("payload", JSONObject()
                            .put("kai", "native")
                            .put("ollama", "external")
                            .put("mode", currentMode)
                            .put("webviewPackage", pkg?.packageName ?: "unknown")
                            .put("webviewVersion", pkg?.versionName ?: "unknown"))
                        .toString()
                )
            }
            "window.mode" -> {
                val mode = parsed.optJSONObject("payload")?.optString("mode") ?: ""
                if (mode in MODES) applyMode(mode)
                emitSignal(BRIDGE_SIGNAL.name, raw)
            }
            "app.background" -> activity?.moveTaskToBack(true)
            "chat.send", "panel.set", "model.select", "cms.select", "world.show", "toy.action", "input.axis", "camera.delta", "app.quit" ->
                emitSignal(BRIDGE_SIGNAL.name, raw)
            else -> Unit
        }
    }
}
