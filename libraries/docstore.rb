require 'net/http'

class Docstore
  def initialize(url)
    m = %r{\w+://(\w+):(\d+)}.match(url)
    host, port = m[1], m[2].to_i
    @http = Net::HTTP.new(host, port)
    @cache = {}
  end

  def get(path)
    if not @cache.has_key?(path)
      fill_cache(path)
    end
    return @cache[path]
  end

  def fill_cache(path)
    response = @http.get(path)
    if response.code == "200"
      @cache[path] = response.body
    end
  end
end
