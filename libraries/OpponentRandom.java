import java.util.HashMap;

public class OpponentRandom {
    public static void main(String[] args) {
        Pubsub pubsub = new Pubsub(args[0], "context");
	String queue = pubsub.subscribe("topic");
	HashMap<String, String> message = new HashMap<String, String>();
	message.put("hello", "java");
	pubsub.publish("topic", message);
	System.out.println(pubsub.getMessage(queue).toString());
	pubsub.consumeTopic("test", new TestConsumer());
    }

}

/* package */ class TestConsumer implements Consumer {
    public TestConsumer() {}
    
    public void consume(HashMap message) {
	String m = message.toString();
	System.out.println(m);
    }
}
