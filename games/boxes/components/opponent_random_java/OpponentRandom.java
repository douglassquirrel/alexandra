import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Random;

public class OpponentRandom {
    public static void main(String[] args) {
	Alexandra alex = new Alexandra(args[0]);
	int index = new Integer(args[1]);
	Mover mover = new Mover(alex, index);
	alex.pubsub.consumeTopic("world", mover);
    }
}

/* package */ class Mover implements Consumer {
    private Alexandra alex;
    private int index;
    private String name;
    private Random random;
    private Integer[][] deltas = new Integer[4][];

    public Mover(Alexandra alex, int index) {
	this.alex = alex;
	this.index = index;
	name = "opponent_random_" + Integer.toString(index);
	random = new Random();
	deltas[0] = new Integer[] {-20,  0};
	deltas[1] = new Integer[] {20,   0};
	deltas[2] = new Integer[] {0,  -20};
	deltas[3] = new Integer[] {0,   20};
    }
    
    public void consume(HashMap world) {
	int tick = decodeInt(world, "tick");
	HashMap entities = (HashMap) world.get("entities");
	HashMap movements = (HashMap) world.get("movements");

	if (!entities.containsKey(name)) {
	    Integer[] position = new Integer[2];
	    int playerStartX = decodeInt(alex.config, "player_start_x");
	    int playerStartY = decodeInt(alex.config, "player_start_y");
	    position[0] = playerStartX + 80 * (index + 1);
	    position[1] = playerStartY;
	    sendMovement(position, position, tick);
	    return;
	}
	HashMap entity = (HashMap) entities.get(name);

	Integer[] delta = new Integer[] {0, 0};
	if (!movements.containsKey(name)) {
	    delta = randomdelta();
	} else {
	    HashMap movement = (HashMap) movements.get(name);
	    Integer[] from = decodePosition(movement, "from");
	    Integer[] to = decodePosition(movement, "to");
	    delta[0] = to[0] - from[0];
	    delta[1] = to[1] - from[1];
	    if (delta[0] == 0 && delta[1] == 0) {
		delta = randomdelta();
	    }
	}

	Integer[] position = decodePosition(entity, "position");
	Integer[] newPosition = new Integer[2];
	newPosition[0] = position[0] + delta[0];
	newPosition[1] = position[1] + delta[1];
	sendMovement(position, newPosition, tick);
    }

    private Integer[] decodePosition(HashMap map, String key) {
	List positionAsList = (List) map.get(key);
	Integer[] position = new Integer[2];
	position[0] = ((Long) positionAsList.get(0)).intValue();
	position[1] = ((Long) positionAsList.get(1)).intValue();
	return position;
    }

    private int decodeInt(HashMap map, String key) {
	return ((Long) map.get(key)).intValue();
    }

    private Integer[] randomdelta() {
	return deltas[random.nextInt(deltas.length)];
    }

    private void sendMovement(Integer[] from, Integer[] to, int tick) {
	HashMap movement = new HashMap();
	movement.put("tick", tick);
	movement.put("entity", "opponent_random");
	movement.put("index", index);
	movement.put("from", Arrays.asList(from));
	movement.put("to", Arrays.asList(to));
	alex.pubsub.publish("movement.opponent_random", movement);
    }
}
