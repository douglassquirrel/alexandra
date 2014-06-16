import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.IOException;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.net.HttpURLConnection;
import java.net.URL;

/* Supports only HTTP connections and JSON marshal/unmarshal. */
public class Pubsub {
    private String rootURL;
    
    public Pubsub(String url, String context) {
	this.rootURL = url + "/contexts/" + context;
    }

    public void publish(String topic, Object message) {
	visitURL(rootURL + "/" + topic, marshal(message), "POST", null); 
    }

    public String subscribe(String topic) {
	return visitURL(rootURL + "/" + topic);
    }

    public void consumeQueue(String queue, Consumer consumer) {
	String url = rootURL + "/queues/" + queue;
	String[][] headers = new String[1][2];
	headers[0][0] = "Patience";
	headers[0][1] = "1";
	while (true) {
	    String message = visitURL(url, null, "GET", headers);
	    if (message != null && message.length() > 0) {
		consumer.consume(unmarshal(message));
	    }
	}
    }

    public void consumeTopic(String topic, Consumer consumer) {
	String queue = subscribe(topic);
	consumeQueue(queue, consumer);
    }

    public void unsubscribe(String queue) {
	visitURL(rootURL + "/queues/" + queue, null, "DELETE", null);
    }

    public Object getMessage(String queue) {
	String message = visitURL(rootURL + "/queues/" + queue, null,
				  "GET", null);
	return unmarshal(message);
    }

    private String visitURL(String url) {
	return visitURL(url, null, "GET", null);
    }

    private String marshal(Object message) {
	return message.toString(); //JSON
    }

    private Object unmarshal(String message) {
	if (message == null) {
	    return null;
	} else {
	    return message; // JSON
	}
    }

    private String visitURL(String url, String data, String method,
			    String[][] headers) {
	try {
	    URL src = new URL(url);
	    HttpURLConnection conn = (HttpURLConnection) src.openConnection();
	    conn.setRequestMethod(method);
	    if (data != null) {
		conn.setDoOutput(true);
		OutputStream outS = conn.getOutputStream();
		OutputStreamWriter out = new OutputStreamWriter(outS);
		out.write(data);
		out.close();
	    }
	    if (headers != null) {
		for (String[] header : headers) {
		    conn.setRequestProperty(header[0], header[1]);
		}
	    }

	    int responseCode = conn.getResponseCode();
	    if (responseCode != 200) {
		return "";
	    }

	    InputStream inS = conn.getInputStream();
	    InputStreamReader inStream = new InputStreamReader(inS);
	    BufferedReader in = new BufferedReader(inStream);
	    StringBuffer response = new StringBuffer();
	    for (String line; (line = in.readLine()) != null;) {
		response.append(line);
	    }
	    in.close();
	    if (response.length() == 0) {
		return null;
	    } else {
		return response.toString();
	    }
	} catch (IOException e) {
	    System.out.println(e);
	}
	return null;
    }
}
