#include "SslProxyServer.h"
#include <cstdlib> // Adicionado para system

SslProxyServer::SslProxyServer(const ProxyConfig& config) 
    : ProxyServer(config), ssl_context_(nullptr) {
}

SslProxyServer::~SslProxyServer() {
    cleanupSSLContext();
}

bool SslProxyServer::initialize() {
    initializeOpenSSL();
    
    if (!initializeSSLContext()) {
        return false;
    }
    
    return ProxyServer::initialize();
}

void SslProxyServer::cleanup() {
    ProxyServer::cleanup();
    cleanupSSLContext();
    cleanupOpenSSL();
}

std::shared_ptr<Client> SslProxyServer::acceptConnection() {
    auto client = ProxyServer::acceptConnection();
    if (!client) {
        return nullptr;
    }
    
    // Perform SSL handshake
    if (!handleSSLHandshake(client->getSocketFd())) {
        return nullptr;
    }
    
    return client;
}

bool SslProxyServer::handleSSLHandshake(int client_fd) {
    SSL* ssl = SSL_new(ssl_context_);
    if (!ssl) {
        LOG_ERROR("Failed to create SSL structure");
        return false;
    }
    
    if (SSL_set_fd(ssl, client_fd) != 1) {
        LOG_ERROR("Failed to set SSL file descriptor");
        SSL_free(ssl);
        return false;
    }
    
    int result = SSL_accept(ssl);
    if (result <= 0) {
        int ssl_error = SSL_get_error(ssl, result);
        LOG_ERROR("SSL handshake failed: " << ssl_error);
        ERR_print_errors_fp(stderr);
        SSL_free(ssl);
        return false;
    }
    
    // SSL handshake successful
    SSL_free(ssl);
    return true;
}

bool SslProxyServer::initializeSSLContext() {
    ssl_context_ = SSL_CTX_new(TLS_server_method());
    if (!ssl_context_) {
        LOG_ERROR("Failed to create SSL context");
        return false;
    }
    
    // Set SSL options
    SSL_CTX_set_options(ssl_context_, SSL_OP_SINGLE_DH_USE | SSL_OP_LEGACY_SERVER_CONNECT); // Adicionado legacy para compat

    // Set cipher list
    if (SSL_CTX_set_cipher_list(ssl_context_, "DEFAULT") != 1) {
        LOG_ERROR("Failed to set cipher list");
        return false;
    }
    
    // Load certificates
    if (!loadCertificates()) {
        return false;
    }
    
    // Load private key
    if (!loadPrivateKey()) {
        return false;
    }
    
    return true;
}

void SslProxyServer::cleanupSSLContext() {
    if (ssl_context_) {
        SSL_CTX_free(ssl_context_);
        ssl_context_ = nullptr;
    }
}

bool SslProxyServer::loadCertificates() {
    if (config_.cert_path.empty()) {
        LOG_WARNING("No cert path provided, generating temp self-signed cert...");
        system("openssl req -new -x509 -days 365 -nodes -out temp.crt -keyout temp.key -subj \"/CN=localhost\" 2>/dev/null");
        config_.cert_path = "temp.crt";
    }
    if (SSL_CTX_use_certificate_file(ssl_context_, config_.cert_path.c_str(), SSL_FILETYPE_PEM) != 1) {
        LOG_ERROR("Failed to load SSL certificate file");
        ERR_print_errors_fp(stderr);
        return false;
    }
    return true;
}

bool SslProxyServer::loadPrivateKey() {
    std::string key_path = config_.cert_path == "temp.crt" ? "temp.key" : config_.cert_path;
    if (SSL_CTX_use_PrivateKey_file(ssl_context_, key_path.c_str(), SSL_FILETYPE_PEM) != 1) {
        LOG_ERROR("Failed to load SSL private key file");
        ERR_print_errors_fp(stderr);
        return false;
    }
    return true;
}

void SslProxyServer::initializeOpenSSL() {
    OPENSSL_init_ssl(OPENSSL_INIT_LOAD_SSL_STRINGS | OPENSSL_INIT_LOAD_CRYPTO_STRINGS, nullptr);
    OPENSSL_init_crypto(OPENSSL_INIT_ADD_ALL_CIPHERS | OPENSSL_INIT_ADD_ALL_DIGESTS, nullptr);
}

void SslProxyServer::cleanupOpenSSL() {
    // Automatico
}
