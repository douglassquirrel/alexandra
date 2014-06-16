import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URL;

/* Supports only HTTP connections and JSON marshal/unmarshal. */
public class Pubsub {
    private String rootURL;
    
    public Pubsub(String url, String context) {
	this.rootURL = url + "/contexts/" + context;
    }

    public String subscribe(String topic) {
	return visitURL(rootURL + "/" + topic);
    }

    private String visitURL(String url) {
	return visitURL(url, null, "GET", null);
    }

    private String visitURL(String url, String data, String method,
			  String[][] headers) {
	try {
	    URL src = new URL(url);
	    HttpURLConnection conn = (HttpURLConnection) src.openConnection();
	    conn.setRequestMethod(method);
	    if (headers != null) {
		for (String[] header : headers) {
		    conn.setRequestProperty(header[0], header[1]);
		}
	    }
	    if (data != null) {
		/* send it */
	    }

	    int responseCode = conn.getResponseCode();
	    if (responseCode != 200) {
		return "";
	    }

	    BufferedReader in
		= new BufferedReader(new InputStreamReader(conn.getInputStream()));
	    StringBuffer response = new StringBuffer();
	    for (String line; (line = in.readLine()) != null;) {
		response.append(line);
	    }
	    in.close();
	    return response.toString();
	} catch (IOException e) {
	    return "";
	}
    }
}
