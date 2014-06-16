public class OpponentRandom {
    public static void main(String[] args) {
        Pubsub pubsub = new Pubsub(args[0], "context");
	String queue = pubsub.subscribe("topic");
	pubsub.publish("topic", "hello java");
	System.out.println(pubsub.getMessage(queue));
	pubsub.consumeTopic("test", new TestConsumer());
    }

}

/* package */ class TestConsumer implements Consumer {
    public TestConsumer() {}
    
    public void consume(Object message) {
	String m = message.toString();
	System.out.println(m);
    }
}
