import org.jetbrains.kotlin.gradle.dsl.JvmTarget

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}
android {
    namespace = "art.eggiebagelface.luhmos.onishell"
    compileSdk = 36
    defaultConfig {
        applicationId = "art.eggiebagelface.luhmos.onishell"
        minSdk = 29
        targetSdk = 36
        versionCode = 1
        versionName = "0.1.0-candidate"
    }
    buildTypes {
        getByName("release") {
            isMinifyEnabled = false
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlin {
        compilerOptions {
            jvmTarget.set(JvmTarget.JVM_17)
        }
    }
}
dependencies {
    implementation("androidx.webkit:webkit:1.17.1")
}

// Source from the EXISTING canonical LuHm frontEnd/.
// Never copy private media/ or arbitrary repository assets.
val syncOniCockpitAssets by tasks.registering(Sync::class) {
    from(rootProject.file("../frontEnd")) {
        include("index.html", "styles.css", "app.js")
        include("jquery/**", "vendor/**")
    }
    into(layout.buildDirectory.dir("generated/oniCockpitAssets/cockpit"))
}
android.sourceSets.getByName("main").assets.srcDir(
    layout.buildDirectory.dir("generated/oniCockpitAssets")
)
tasks.named("preBuild") { dependsOn(syncOniCockpitAssets) }
