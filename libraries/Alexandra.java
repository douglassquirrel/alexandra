import java.util.HashMap;

public class Alexandra {
    public String gameID;
    public Pubsub pubsub;
    public HashMap config;

    public Alexandra(String gameID) {
	this.gameID = gameID;
	String pubsubURL = System.getenv("ALEXANDRA_PUBSUB");
	pubsub = new Pubsub(pubsubURL, "games-" + gameID);
	config = null;
	while (config == null) {
	    config = pubsub.getCurrentMessage("game.json");
	}
    }
}