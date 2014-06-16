public class OpponentRandom {
    public static void main(String[] args) {
        Pubsub pubsub = new Pubsub(args[0], "context");
	System.out.println(pubsub.subscribe("topic"));
    }
}
