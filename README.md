# Proxy_Server
NOTES:
1. THE PROXY SERVER IS IN test.py
2. Proxy is currently not working 
Proxy design:
1. Proxy listens on port 2009 for incoming connections from browser (2009 is just a random port i chose)
2. If incoming request is for HTTP, than directly forward request to designated server
3a. If incoming request is HTTPS, start performing an HTTP tunnel (for refrence: https://en.wikipedia.org/wiki/HTTP_tunnel)
3b. After tunnel established, blindly forward bytes to and from server to browser
