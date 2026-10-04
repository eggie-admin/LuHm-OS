package art.eggiebagelface.luhmos.kaiwebview

import android.graphics.Color
import android.net.Uri
import android.view.View
import android.view.ViewGroup
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
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

class KAIWebView(godot: Godot) : GodotPlugin(godot) {
    companion object {
        private const val ORIGIN = "https://appassets.androidplatform.net"
        private const val START_URL = "$ORIGIN/assets/cockpit/index.html"
        private val BRIDGE_SIGNAL = SignalInfo("bridge_message", String::class.java)
    }

    private var webView: WebView? = null

    override fun getPluginName() = BuildConfig.GODOT_PLUGIN_NAME

    override fun getPluginSignals() = setOf(BRIDGE_SIGNAL)

    @UsedByGodot
    fun showCockpit() {
        runOnHostThread {
            ensureWebView().visibility = View.VISIBLE
        }
    }

    @UsedByGodot
    fun hideCockpit() {
        runOnHostThread {
            webView?.visibility = View.GONE
        }
    }

    @UsedByGodot
    fun isCockpitReady(): Boolean = webView != null

    @UsedByGodot
    fun getSystemProfile(): String {
        val host = activity ?: return JSONObject()
            .put("schema", "luhm.samsung.system-profile.v1")
            .put("available", false)
            .toString()
        return SamsungSystemProfile.snapshot(host).toString()
    }

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

    private fun ensureWebView(): WebView {
        webView?.let { return it }
        val host = activity ?: error("KAIWebView host activity unavailable")
        val loader = WebViewAssetLoader.Builder()
            .addPathHandler("/assets/", WebViewAssetLoader.AssetsPathHandler(host))
            .build()

        val view = WebView(host)
        view.setBackgroundColor(Color.TRANSPARENT)
        view.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = false
            allowFileAccess = false
            allowContentAccess = false
            mixedContentMode = WebSettings.MIXED_CONTENT_NEVER_ALLOW
            cacheMode = WebSettings.LOAD_NO_CACHE
            setSupportMultipleWindows(false)
        }

        view.webViewClient = object : WebViewClient() {
            override fun shouldInterceptRequest(
                view: WebView?,
                request: WebResourceRequest?
            ): WebResourceResponse? = request?.url?.let(loader::shouldInterceptRequest)

            override fun shouldOverrideUrlLoading(
                view: WebView?,
                request: WebResourceRequest?
            ): Boolean {
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
        root.addView(
            view,
            ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )
        )
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

        when (parsed.optString("type")) {
            "status.request" -> {
                val host = activity
                val systemProfile = if (host == null) {
                    JSONObject()
                        .put("schema", "luhm.samsung.system-profile.v1")
                        .put("available", false)
                } else {
                    SamsungSystemProfile.snapshot(host)
                }
                replyProxy.postMessage(
                    JSONObject()
                        .put("schema", "luhm.bridge.reply.v1")
                        .put("type", "status")
                        .put(
                            "payload",
                            JSONObject()
                                .put("kai", "native")
                                .put("ollama", "external")
                                .put("system", systemProfile)
                        )
                        .toString()
                )
            }
            "chat.send", "panel.set", "model.select", "cms.select" ->
                emitSignal(BRIDGE_SIGNAL.name, raw)
            else -> Unit
        }
    }
}
