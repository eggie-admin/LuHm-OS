package art.eggiebagelface.luhmos.campaignpreview;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import androidx.webkit.WebViewAssetLoader;

public final class MainActivity extends Activity {
    private WebView webView;
    private View fullscreen;
    private WebChromeClient.CustomViewCallback fullscreenCallback;
    private static final String HOME = "https://appassets.androidplatform.net/assets/index.html";
    private static final String LOCAL_HOST = "appassets.androidplatform.net";

    @Override public void onCreate(Bundle saved) {
        super.onCreate(saved);
        getWindow().setStatusBarColor(Color.rgb(23,19,31));
        getWindow().setNavigationBarColor(Color.rgb(23,19,31));
        webView = new WebView(this);
        webView.setBackgroundColor(Color.rgb(23,19,31));
        setContentView(webView);
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(false);
        settings.setAllowContentAccess(false);
        settings.setAllowFileAccessFromFileURLs(false);
        settings.setAllowUniversalAccessFromFileURLs(false);
        settings.setMediaPlaybackRequiresUserGesture(true);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        settings.setSupportMultipleWindows(false);
        settings.setJavaScriptCanOpenWindowsAutomatically(false);

        final WebViewAssetLoader local = new WebViewAssetLoader.Builder()
            .addPathHandler("/assets/", new WebViewAssetLoader.AssetsPathHandler(this)).build();

        webView.setWebViewClient(new WebViewClient() {
            @Override public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                return local.shouldInterceptRequest(request.getUrl());
            }
            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri uri = request.getUrl();
                if ("https".equalsIgnoreCase(uri.getScheme()) && LOCAL_HOST.equalsIgnoreCase(uri.getHost())) return false;
                // User-initiated YouTube embeds retain their own unobstructed player.
                if (!request.isForMainFrame()) return false;
                if ("https".equalsIgnoreCase(uri.getScheme())) {
                    try {
                        startActivity(new Intent(Intent.ACTION_VIEW, uri).addCategory(Intent.CATEGORY_BROWSABLE));
                    } catch (Exception ignored) { }
                }
                return true;
            }
        });
        webView.setWebChromeClient(new WebChromeClient() {
            @Override public void onShowCustomView(View view, CustomViewCallback cb) {
                if (fullscreen != null) { cb.onCustomViewHidden(); return; }
                fullscreen = view;
                fullscreenCallback = cb;
                ((ViewGroup) getWindow().getDecorView()).addView(view,
                    new ViewGroup.LayoutParams(-1, -1));
                webView.setVisibility(View.GONE);
            }
            @Override public void onHideCustomView() { closeFullscreen(); }
        });
        webView.loadUrl(HOME);
    }
    private void closeFullscreen() {
        if (fullscreen == null) return;
        ((ViewGroup) getWindow().getDecorView()).removeView(fullscreen);
        fullscreen = null;
        webView.setVisibility(View.VISIBLE);
        if (fullscreenCallback != null) fullscreenCallback.onCustomViewHidden();
        fullscreenCallback = null;
    }
    @Override public void onBackPressed() {
        if (fullscreen != null) { closeFullscreen(); return; }
        if (webView != null && webView.canGoBack()) { webView.goBack(); return; }
        super.onBackPressed();
    }
    @Override protected void onDestroy() {
        if (webView != null) { webView.destroy(); webView = null; }
        super.onDestroy();
    }
}
