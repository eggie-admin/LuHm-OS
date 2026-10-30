package art.eggiebagelface.luhmos.onishell

import android.app.Activity
import android.os.Bundle
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.FrameLayout
import androidx.webkit.WebViewAssetLoader
import java.io.ByteArrayInputStream

/**
 * Local, unprivileged preview of the EXISTING LuHm cockpit.
 * There is no network permission, JavaScript interface, or shell bridge.
 */
class CockpitActivity : Activity() {
    private lateinit var web: WebView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val loader = WebViewAssetLoader.Builder()
            .addPathHandler("/assets/", WebViewAssetLoader.AssetsPathHandler(this))
            .build()
        web = WebView(this).apply {
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true
            settings.allowFileAccess = false
            settings.allowContentAccess = false
            settings.javaScriptCanOpenWindowsAutomatically = false
            settings.setSupportMultipleWindows(false)
            settings.mixedContentMode = android.webkit.WebSettings.MIXED_CONTENT_NEVER_ALLOW
            webViewClient = object : WebViewClient() {
                override fun shouldInterceptRequest(
                    view: WebView,
                    request: WebResourceRequest
                ): WebResourceResponse {
                    val uri = request.url
                    if (uri.scheme != "https" ||
                        uri.host != "appassets.androidplatform.net" ||
                        !uri.path.orEmpty().startsWith("/assets/cockpit/")) {
                        return blocked()
                    }
                    return loader.shouldInterceptRequest(uri) ?: blocked()
                }
                override fun shouldOverrideUrlLoading(
                    view: WebView,
                    request: WebResourceRequest
                ): Boolean = true // No external navigation
            }
            loadUrl("https://appassets.androidplatform.net/assets/cockpit/index.html")
        }
        val wrapper = FrameLayout(this)
        wrapper.setBackgroundColor(android.graphics.Color.rgb(16, 13, 28))
        wrapper.addView(web)
        setContentView(wrapper)
    }

    private fun blocked(): WebResourceResponse =
        WebResourceResponse("text/plain", "UTF-8", 403, "Forbidden",
            emptyMap(), ByteArrayInputStream(ByteArray(0)))

    override fun onDestroy() {
        web.destroy()
        super.onDestroy()
    }
}
