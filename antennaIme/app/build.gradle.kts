import org.jetbrains.kotlin.gradle.dsl.JvmTarget

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "art.eggiebagelface.luhmos.antenna"
    compileSdk = 36
    defaultConfig {
        applicationId = "art.eggiebagelface.luhmos.antenna"
        minSdk = 26
        targetSdk = 36
        versionCode = 1
        versionName = "0.1.0-candidate"
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlin { compilerOptions { jvmTarget.set(JvmTarget.JVM_17) } }
}
