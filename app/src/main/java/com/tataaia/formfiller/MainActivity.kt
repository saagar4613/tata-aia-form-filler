package com.tataaia.formfiller

import android.Manifest
import android.annotation.SuppressLint
import android.app.AlertDialog
import android.content.Context
import android.content.Intent
import android.content.SharedPreferences
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.os.Handler
import android.os.Looper
import android.webkit.*
import android.widget.EditText
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.core.content.FileProvider
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File
import java.io.FileOutputStream
import java.io.InputStream
import java.net.HttpURLConnection
import java.net.URL

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView
    private lateinit var swipeRefresh: SwipeRefreshLayout
    private lateinit var prefs: SharedPreferences
    private var fileUploadCallback: ValueCallback<Array<Uri>>? = null

    companion object {
        private const val PREFS_NAME = "TataAIAPrefs"
        private const val KEY_SERVER_URL = "server_url"
        const val DEFAULT_SERVER_URL = "https://insider-appreciated-fourth-burner.trycloudflare.com"
    }

    private val filePickerLauncher = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->
        if (result.resultCode == RESULT_OK) {
            val intent = result.data
            val uris: Array<Uri>? = when {
                intent?.clipData != null && intent.clipData!!.itemCount > 0 -> {
                    val count = intent.clipData!!.itemCount
                    Array(count) { i -> intent.clipData!!.getItemAt(i).uri }
                }
                intent?.data != null -> arrayOf(intent.data!!)
                else -> null
            }
            fileUploadCallback?.onReceiveValue(uris)
        } else {
            fileUploadCallback?.onReceiveValue(null)
        }
        fileUploadCallback = null
    }

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        prefs = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        webView = findViewById(R.id.webView)
        swipeRefresh = findViewById(R.id.swipeRefresh)

        checkPermissions()
        setupWebView()

        swipeRefresh.setOnRefreshListener {
            webView.reload()
        }

        // Load local asset immediately for instant 0.05s startup (NO WHITE SCREEN)
        webView.loadUrl("file:///android_asset/www/index.html")
    }

    private fun checkPermissions() {
        val permissions = mutableListOf(
            Manifest.permission.CAMERA
        )
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            permissions.add(Manifest.permission.READ_MEDIA_IMAGES)
        } else {
            permissions.add(Manifest.permission.READ_EXTERNAL_STORAGE)
            permissions.add(Manifest.permission.WRITE_EXTERNAL_STORAGE)
        }

        val needed = permissions.filter {
            ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED
        }
        if (needed.isNotEmpty()) {
            ActivityCompat.requestPermissions(this, needed.toTypedArray(), 101)
        }
    }

    @SuppressLint("SetJavaScriptEnabled")
    private fun setupWebView() {
        val settings = webView.settings
        settings.javaScriptEnabled = true
        settings.domStorageEnabled = true
        settings.databaseEnabled = true
        settings.allowFileAccess = true
        settings.allowContentAccess = true
        settings.useWideViewPort = true
        settings.loadWithOverviewMode = true
        settings.setSupportZoom(true)
        settings.builtInZoomControls = true
        settings.displayZoomControls = false
        settings.cacheMode = WebSettings.LOAD_DEFAULT

        // Register Native Android Bridge
        webView.addJavascriptInterface(WebAppInterface(this), "AndroidBridge")

        webView.webViewClient = object : WebViewClient() {
            override fun onPageFinished(view: WebView?, url: String?) {
                swipeRefresh.isRefreshing = false
                super.onPageFinished(view, url)
            }

            override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
                val url = request?.url?.toString() ?: return false

                // Handle external schemes (whatsapp, tel, mailto, intent)
                if (url.startsWith("whatsapp:") || url.startsWith("intent:") ||
                    url.startsWith("mailto:") || url.startsWith("tel:") ||
                    url.contains("api.whatsapp.com")) {
                    try {
                        val intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
                        startActivity(intent)
                        return true
                    } catch (e: Exception) {
                        Toast.makeText(this@MainActivity, "App not found to open link", Toast.LENGTH_SHORT).show()
                        return true
                    }
                }
                return false
            }
        }

        webView.webChromeClient = object : WebChromeClient() {
            override fun onShowFileChooser(
                mWebView: WebView?,
                filePathCallback: ValueCallback<Array<Uri>>?,
                fileChooserParams: FileChooserParams?
            ): Boolean {
                fileUploadCallback?.onReceiveValue(null)
                fileUploadCallback = filePathCallback

                val isMultiple = fileChooserParams?.mode == WebChromeClient.FileChooserParams.MODE_OPEN_MULTIPLE

                val intent = Intent(Intent.ACTION_GET_CONTENT).apply {
                    type = "*/*"
                    putExtra(Intent.EXTRA_MIME_TYPES, arrayOf("image/*", "application/pdf"))
                    putExtra(Intent.EXTRA_ALLOW_MULTIPLE, isMultiple)
                    addCategory(Intent.CATEGORY_OPENABLE)
                }

                try {
                    val title = if (isMultiple) "Select Photos (Hold to multi-select)" else "Select Photo"
                    val chooser = Intent.createChooser(intent, title)
                    filePickerLauncher.launch(chooser)
                } catch (e: Exception) {
                    fileUploadCallback = null
                    Toast.makeText(this@MainActivity, "Cannot open file picker", Toast.LENGTH_SHORT).show()
                    return false
                }
                return true
            }
        }
    }

    /**
     * JavaScript Bridge exposing native Android sharing and file capabilities.
     */
    inner class WebAppInterface(private val context: Context) {

        @JavascriptInterface
        fun getServerUrl(): String {
            val saved = prefs.getString(KEY_SERVER_URL, null)
            if (saved == null || saved.contains("10.127.47.178") || saved.contains("uniprotkb") || (saved.contains("trycloudflare.com") && saved != DEFAULT_SERVER_URL)) {
                prefs.edit().putString(KEY_SERVER_URL, DEFAULT_SERVER_URL).apply()
                return DEFAULT_SERVER_URL
            }
            return saved
        }

        @JavascriptInterface
        fun setServerUrl(newUrl: String) {
            val clean = newUrl.trim()
            val finalUrl = if (!clean.startsWith("http")) "http://$clean" else clean
            prefs.edit().putString(KEY_SERVER_URL, finalUrl).apply()
            showToast("Server URL updated: $finalUrl")
        }

        @JavascriptInterface
        fun promptServerConfig() {
            Handler(Looper.getMainLooper()).post {
                val current = getServerUrl()
                val input = EditText(this@MainActivity).apply {
                    setText(current)
                    hint = DEFAULT_SERVER_URL
                }
                AlertDialog.Builder(this@MainActivity)
                    .setTitle("Configure Server Address")
                    .setMessage("Enter the IP address and port of your PC server:")
                    .setView(input)
                    .setPositiveButton("Save") { _, _ ->
                        val entered = input.text.toString().trim()
                        if (entered.isNotEmpty()) {
                            setServerUrl(entered)
                            webView.evaluateJavascript("if (typeof updateServerUrl === 'function') updateServerUrl('$entered');", null)
                        }
                    }
                    .setNegativeButton("Cancel", null)
                    .show()
            }
        }

        @JavascriptInterface
        fun sharePdf(downloadUrl: String, filename: String, customerName: String) {
            val caption = customerName.trim().uppercase()
            val cleanFilename = if (caption.isNotEmpty()) "${caption.replace(Regex("[^A-Za-z0-9]"), "_")}.pdf" else filename
            showToast("Preparing PDF for sharing...")
            CoroutineScope(Dispatchers.IO).launch {
                try {
                    val fullUrl = resolveFullUrl(downloadUrl)
                    val pdfFile = downloadPdfFile(fullUrl, cleanFilename)

                    withContext(Dispatchers.Main) {
                        if (pdfFile != null && pdfFile.exists() && pdfFile.length() > 0) {
                            val uri = FileProvider.getUriForFile(
                                context,
                                "${context.packageName}.fileprovider",
                                pdfFile
                            )

                            val shareIntent = Intent(Intent.ACTION_SEND).apply {
                                type = "application/pdf"
                                putExtra(Intent.EXTRA_STREAM, uri)
                                putExtra(Intent.EXTRA_SUBJECT, caption)
                                putExtra(Intent.EXTRA_TEXT, caption)
                                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                            }

                            val chooser = Intent.createChooser(shareIntent, caption)
                            context.startActivity(chooser)
                        } else {
                            showToast("Error preparing PDF for sharing")
                        }
                    }
                } catch (e: Exception) {
                    withContext(Dispatchers.Main) {
                        showToast("Sharing failed: ${e.message}")
                    }
                }
            }
        }

        @JavascriptInterface
        fun downloadPdf(downloadUrl: String, filename: String) {
            val cleanFilename = if (!filename.endsWith(".pdf", ignoreCase = true)) "$filename.pdf" else filename
            showToast("Downloading $cleanFilename...")
            CoroutineScope(Dispatchers.IO).launch {
                try {
                    val fullUrl = resolveFullUrl(downloadUrl)
                    val downloadsDir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS)
                    val targetFile = File(downloadsDir, cleanFilename)

                    val downloaded = downloadToFile(fullUrl, targetFile)
                    withContext(Dispatchers.Main) {
                        if (downloaded) {
                            showToast("PDF saved to Downloads folder: $cleanFilename")
                            // Offer to open
                            promptOpenDownloadedPdf(targetFile)
                        } else {
                            showToast("Failed to download PDF")
                        }
                    }
                } catch (e: Exception) {
                    withContext(Dispatchers.Main) {
                        showToast("Download failed: ${e.message}")
                    }
                }
            }
        }

        @JavascriptInterface
        fun openPdf(downloadUrl: String, filename: String) {
            CoroutineScope(Dispatchers.IO).launch {
                try {
                    val fullUrl = resolveFullUrl(downloadUrl)
                    val pdfFile = downloadPdfFile(fullUrl, filename)
                    withContext(Dispatchers.Main) {
                        if (pdfFile != null && pdfFile.exists()) {
                            val uri = FileProvider.getUriForFile(
                                context,
                                "${context.packageName}.fileprovider",
                                pdfFile
                            )
                            val viewIntent = Intent(Intent.ACTION_VIEW).apply {
                                setDataAndType(uri, "application/pdf")
                                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                            }
                            context.startActivity(Intent.createChooser(viewIntent, "Open PDF with"))
                        }
                    }
                } catch (e: Exception) {
                    withContext(Dispatchers.Main) {
                        showToast("Cannot open PDF: ${e.message}")
                    }
                }
            }
        }

        private fun resolveFullUrl(urlStr: String): String {
            if (urlStr.startsWith("http://") || urlStr.startsWith("https://")) {
                return urlStr
            }
            val base = getServerUrl().trimEnd('/')
            val path = urlStr.trimStart('/')
            return "$base/$path"
        }

        private fun downloadPdfFile(urlStr: String, filename: String): File? {
            val cacheFolder = File(context.cacheDir, "tata_aia_forms")
            if (!cacheFolder.exists()) cacheFolder.mkdirs()

            val target = File(cacheFolder, filename)
            val success = downloadToFile(urlStr, target)
            return if (success) target else null
        }

        private fun downloadToFile(urlStr: String, targetFile: File): Boolean {
            var conn: HttpURLConnection? = null
            var input: InputStream? = null
            var output: FileOutputStream? = null
            return try {
                val url = URL(urlStr)
                conn = url.openConnection() as HttpURLConnection
                conn.connectTimeout = 15000
                conn.readTimeout = 30000
                conn.requestMethod = "GET"
                conn.connect()

                if (conn.responseCode == HttpURLConnection.HTTP_OK) {
                    input = conn.inputStream
                    output = FileOutputStream(targetFile)
                    val buffer = ByteArray(8192)
                    var bytesRead: Int
                    while (input.read(buffer).also { bytesRead = it } != -1) {
                        output.write(buffer, 0, bytesRead)
                    }
                    output.flush()
                    true
                } else {
                    false
                }
            } catch (e: Exception) {
                false
            } finally {
                output?.close()
                input?.close()
                conn?.disconnect()
            }
        }

        private fun promptOpenDownloadedPdf(file: File) {
            AlertDialog.Builder(this@MainActivity)
                .setTitle("PDF Downloaded")
                .setMessage("Saved to Downloads/${file.name}.\nWould you like to open it now?")
                .setPositiveButton("Open") { _, _ ->
                    val uri = FileProvider.getUriForFile(
                        this@MainActivity,
                        "${packageName}.fileprovider",
                        file
                    )
                    val viewIntent = Intent(Intent.ACTION_VIEW).apply {
                        setDataAndType(uri, "application/pdf")
                        addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                    }
                    try {
                        startActivity(Intent.createChooser(viewIntent, "Open PDF with"))
                    } catch (e: Exception) {
                        showToast("No PDF viewer installed")
                    }
                }
                .setNegativeButton("Done", null)
                .show()
        }

        private fun showToast(msg: String) {
            Handler(Looper.getMainLooper()).post {
                Toast.makeText(context, msg, Toast.LENGTH_SHORT).show()
            }
        }
    }

    override fun onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack()
        } else {
            super.onBackPressed()
        }
    }
}
