import java.util.HashMap;

public class OpponentRandom {
    public static void main(String[] args) {
	Alexandra alex = new Alexandra("game1234");
	String queue = alex.pubsub.subscribe("topic");
	HashMap<String, String> message = new HashMap<String, String>();
	message.put("hello", "java");
	alex.pubsub.publish("topic", message);
	System.out.println(alex.pubsub.getMessage(queue).toString());
	alex.pubsub.consumeTopic("test", new TestConsumer());
    }

}

/* package */ class TestConsumer implements Consumer {
    public TestConsumer() {}
    
    public void consume(HashMap message) {
	String m = message.toString();
	System.out.println(m);
    }
}
