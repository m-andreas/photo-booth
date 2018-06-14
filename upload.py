import flickrapi
FLICKR_PUBLIC = '16b19f04436708b6b4b8465b9e12b5f0'
FLICKR_SECRET = '0a67d76bc0a6bf8a'
flickr = flickrapi.FlickrAPI(api_key, api_secret)
flickr.authenticate_via_browser(perms='write')
flickr.upload(filename="/tmp/c.jpg", title="test", is_public=1, format="rest")
