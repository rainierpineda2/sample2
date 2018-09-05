when HTTP_REQUEST {
   switch [string tolower [HTTP::host]] {
            "old1.jnjlab.com" { HTTP::redirect "https://new1.jnjlab.com" }
            "old2.jnjlab.com" { HTTP::redirect "https://new2.jnjlab.com" }
         }
}
