import org.jetbrains.kotlin.gradle.dsl.JvmTarget

// Explicit minimal Android assets: no prototypes, npm sources, private files,
// remote media or arbitrary frontEnd/ trees in the release AAR.
val cockpitAssetPaths = listOf(
    "index.html",
    "styles.css",
    "app.js",
    "vendor/jquery-3.7.1.min.js",
    "vendor/jquery-LICENSE.txt",
    "jquery/luhm.codingRoleplay.js",
    "jquery/luhm.parallax.js",
    "jquery/luhm.cockpit.js",
    "jquery/luhm.cast.js",
)
val cockpitAssetsDirectory = layout.buildDirectory.dir("generated/luhmCockpitAssets")
val stageCockpitAssets by tasks.registering(Sync::class) {
    from(rootProject.file("../frontEnd")) {
        include(*cockpitAssetPaths.toTypedArray())
    }
    into(cockpitAssetsDirectory)
    doLast {
        val base = cockpitAssetsDirectory.get().asFile
        val actual = base.walkTopDown().filter { it.isFile }
            .map { it.relativeTo(base).invariantSeparatorsPath }.toSet()
        val expected = cockpitAssetPaths.toSet()
        if (actual != expected) {
            throw GradleException("RED_COCKPIT_ASSETS: missing=${expected - actual}, extra=${actual - expected}")
        }
    }
}

plugins {
    id("com.android.library")
    id("org.jetbrains.kotlin.android")
}

val pluginName = "AndroidWeb3Cockpit"
val pluginPackageName = "art.eggiebagelface.luhmos.web3"

android {
    namespace = pluginPackageName
    compileSdk = 36

    buildFeatures {
        buildConfig = true
    }

    defaultConfig {
        minSdk = 24
        manifestPlaceholders["godotPluginName"] = pluginName
        manifestPlaceholders["godotPluginPackageName"] = pluginPackageName
        buildConfigField("String", "GODOT_PLUGIN_NAME", "\"$pluginName\"")
        setProperty("archivesBaseName", pluginName)
    }

    sourceSets {
        getByName("main") {
            // Only the verified local cockpit bundle enters the Android AAR.
            assets.srcDir(cockpitAssetsDirectory)
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
    implementation("org.godotengine:godot:4.7.2.stable")
    implementation("androidx.webkit:webkit:1.17.1")
}

val addonsDir = rootProject.file("../addons/AndroidWeb3Cockpit")

val syncExportScripts by tasks.registering(Copy::class) {
    from("export_scripts_template")
    into(addonsDir)
}

val copyDebugAar by tasks.registering(Copy::class) {
    from(layout.buildDirectory.dir("outputs/aar"))
    include("$pluginName-debug.aar")
    into(addonsDir.resolve("bin/debug"))
}

val copyReleaseAar by tasks.registering(Copy::class) {
    from(layout.buildDirectory.dir("outputs/aar"))
    include("$pluginName-release.aar")
    into(addonsDir.resolve("bin/release"))
}

tasks.named("assemble").configure {
    finalizedBy(syncExportScripts, copyDebugAar, copyReleaseAar)
}

// Explicit dependency edge: staging must finish before either Android AAR
// variant merges assets. Missing pinned jQuery or license fails closed.
tasks.configureEach {
    if (name.startsWith("merge") && name.endsWith("Assets")) {
        dependsOn(stageCockpitAssets)
    }
}
