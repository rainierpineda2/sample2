when HTTP_REQUEST { 
   switch [string tolower [HTTP::host]] {
      "symphonysb.jnj.com" {
          if { [string tolower [HTTP::uri]] equals "/" } {
                HTTP::redirect "https://itsusmpl00026.jnj.com:14306/reliance_sand/reliance" }
      }
   }
}
