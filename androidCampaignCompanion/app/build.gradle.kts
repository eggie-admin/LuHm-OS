plugins { id("com.android.application") }
android {
    namespace = "art.eggiebagelface.luhmos.campaignpreview"
    compileSdk = 36
    defaultConfig {
        applicationId = "art.eggiebagelface.luhmos.campaignpreview"
        minSdk = 26
        targetSdk = 36
        versionCode = (providers.gradleProperty("previewVersionCode").orNull?.toIntOrNull() ?: 300001)
        versionName = "0.1.0-source-preview"
    }
    buildTypes {
        getByName("release") {
            isMinifyEnabled = false
            isShrinkResources = false
            // Owner-held PKCS12 only, never store key material or debug signing here.
        }
    }
    sourceSets.getByName("main").assets.srcDir(rootProject.file("../publicationSite"))
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}
dependencies { implementation("androidx.webkit:webkit:1.18.0") }
