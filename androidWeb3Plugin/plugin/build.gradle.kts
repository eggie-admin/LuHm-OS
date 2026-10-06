import org.jetbrains.kotlin.gradle.dsl.JvmTarget

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
            assets.srcDir("../../frontEnd")
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
