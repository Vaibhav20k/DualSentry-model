package middleware

import (
	"net"
	"net/http"
	"strings"
)

func ClientIP(r *http.Request) string {

	// Reverse proxies (Nginx, Traefik, Cloudflare)
	if forwarded := r.Header.Get("X-Forwarded-For"); forwarded != "" {
		parts := strings.Split(forwarded, ",")
		return strings.TrimSpace(parts[0])
	}

	// Load balancers
	if realIP := r.Header.Get("X-Real-IP"); realIP != "" {
		return realIP
	}

	// Local development
	ip, _, err := net.SplitHostPort(r.RemoteAddr)
	if err == nil {
		return ip
	}

	return r.RemoteAddr
}
