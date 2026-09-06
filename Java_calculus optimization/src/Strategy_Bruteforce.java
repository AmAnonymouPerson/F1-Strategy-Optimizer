import java.util.ArrayList;
import java.util.Arrays;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.File;


public class Strategy_Bruteforce {
    static String[] compounds = {"Soft" , "Medium" , "Hard"};

    public static void main(String[] args) throws Exception {
        ObjectMapper mapper = new ObjectMapper();

        InputData input = mapper.readValue(new File("input.json"), InputData.class);

        ArrayList<String[]> final_list = getIdeas(input.constants, input.pit_time_lost, input.total_laps, input.excluded_compound);

        mapper.writeValue(new File("output.json"), final_list);

    }


    public static ArrayList<String[]> getIdeas(double[][] constants, double pit_time_lost, int total_laps, int excluded_compound) {

        ArrayList<String[]> ideas = new ArrayList<>();

        ideas.addAll(optimise_one_stop(constants, pit_time_lost, total_laps, excluded_compound));
        ideas.addAll(optimise_two_stops(constants, pit_time_lost, total_laps, excluded_compound));
        ideas.addAll(optimise_three_stops(constants, pit_time_lost, total_laps, excluded_compound));

        ArrayList<String[]> ordered_list = new ArrayList<>();

        int size = ideas.size();
        for(int i = 0 ; i < size; i++){
            double min = Integer.MAX_VALUE;
            int test = 0;
            for(int j = 0 ; j< ideas.size() ; j++){
                if(Double.parseDouble(ideas.get(j)[2])<min){
                    min = Double.parseDouble(ideas.get(j)[2]);
                    test = j;
                }
            }
            ordered_list.add(ideas.get(test));
            ideas.remove(test);
        }


        return ordered_list;
    }
    public static ArrayList<String[]> optimise_one_stop(double[][] constants, double pit_time_lost, int total_laps, int excluded_compound){

        ArrayList<String[]> one_stops = new ArrayList<>();

        for(int i = 0 ; i < 3 ; i++){
            for(int j = i ; j <3 ; j++){
                if(i==j || i == excluded_compound || j == excluded_compound){
                    continue;
                }
                one_stops.add(optimal_one_stop_run(constants, pit_time_lost, total_laps, i, j));
            }
        }

        return one_stops;
    }
    public static String [] optimal_one_stop_run(double[][] constants, double pit_time_lost, int total_laps, int t1, int t2){
        double min = Integer.MAX_VALUE;
        int x;
        int y;
        double time;
        int xf = 0;
        int yf = 0;
        for(int i = 1 ; i < total_laps ; i++ ){
            x = i ;
            y = total_laps- i ;
            double tire_1_time = (constants[t1][0]/3)* x * x * x + (constants[t1][1]/2)* x * x + constants[t1][2]* x;
            double tire_2_time = (constants[t2][0]/3)* y * y * y + (constants[t2][1]/2)* y * y + constants[t2][2]* y;
            time = tire_1_time+tire_2_time+pit_time_lost;
            if(time <min){
                min = time;
                xf = x;
                yf = y;
            }
        }
        time=min;
        String type_and_compounds = "One stop " + compounds[t1] + "-" + compounds[t2];
        return new String[]{type_and_compounds, xf + "-" +  yf , String.valueOf(time)};
    }
    public static ArrayList<String[]> optimise_two_stops(double[][] constants, double pit_time_lost, int total_laps, int excluded_compound) {

        ArrayList<String[]> two_stops = new ArrayList<>();

        for (int i = 0; i < 3; i++) {
            for (int j = i; j < 3; j++) {
                for (int k = j; k < 3; k++) {
                    if ((i == j && j == k) || i == excluded_compound || j == excluded_compound || k == excluded_compound) {
                        continue;
                    }
                    two_stops.add(optimal_two_stop_run(constants, pit_time_lost, total_laps, i , j , k));
                }
            }
        }
        return two_stops;
    }
    public static String[] optimal_two_stop_run(double[][] constants, double pit_time_lost, int total_laps, int t1, int t2 , int t3){
        double min = Integer.MAX_VALUE;
        int x;
        int y;
        int z;
        int xf = 0;
        int yf = 0;
        int zf = 0;
        double time = 0 ;
        for(int i = 1 ; i <(total_laps-1) ; i++ ){
            for(int j = 1 ; j <(total_laps-i) ; j++ ){
                x = i;
                y = j;
                z = total_laps - x - y ;
                double tire_1_time = constants[t1][0]* x * x * x/3 + constants[t1][1]* x * x/2 + constants[t1][2]* x;
                double tire_2_time = constants[t2][0]* y * y * y/3 + constants[t2][1]* y * y/2 + constants[t2][2]* y;
                double tire_3_time = constants[t3][0]* z * z * z/3 + constants[t3][1]* z * z/2 + constants[t3][2]* z;
                time = tire_1_time+tire_2_time+tire_3_time+pit_time_lost*2;
                if(time <min){
                    min = time;
                    xf = x;
                    yf = y;
                    zf = z;
                }
            }
        }
        time=min;

        String type_and_compounds = "Two stop "+ compounds[t1]+"-"+compounds[t2]+"-"+compounds[t3];
        String pit_laps = xf+"-"+yf+"-"+zf;
        return new String[]{type_and_compounds , pit_laps , String.valueOf(time)};
    }
    public static ArrayList<String[]> optimise_three_stops(double[][] constants, double pit_time_lost, int total_laps, int excluded_compound) {

        ArrayList<String[]> three_stops = new ArrayList<>();

        for (int i = 0; i < 3; i++) {
            for (int j = i; j < 3; j++) {
                for (int k = j; k < 3; k++) {
                    for (int l = k; l < 3; l++) {
                        if ((i == j && j == k && k == l) || i == excluded_compound || j == excluded_compound || k == excluded_compound || l == excluded_compound) {
                            continue;
                        }
                        three_stops.add(optimal_three_stop_run(constants, pit_time_lost, total_laps, i, j, k, l));
                    }
                }
            }
        }
        return three_stops;
    }
    public static String [] optimal_three_stop_run(double[][] constants, double pit_time_lost, int total_laps, int t1, int t2 , int t3 , int t4){
        double min = Integer.MAX_VALUE;
        int x;
        int y;
        int z;
        int w;
        int xf = 0;
        int yf = 0;
        int zf = 0;
        int wf = 0;
        double time = 0 ;
        for(int i = 1 ; i <(total_laps-2) ; i++ ){
            for(int j = 1 ; j <(total_laps-i-1) ; j++ ){
                for(int k = 1 ; k <(total_laps-i-j) ; k++ ){
                    x = i;
                    y = j;
                    z = k;
                    w = total_laps - x- y -z;
                    double tire_1_time = constants[t1][0]* x * x * x/3 + constants[t1][1]* x * x/2 + constants[t1][2]* x;
                    double tire_2_time = constants[t2][0]* y * y * y/3 + constants[t2][1]* y * y/2 + constants[t2][2]* y;
                    double tire_3_time = constants[t3][0]* z * z * z/3 + constants[t3][1]* z * z/2 + constants[t3][2]* z;
                    double tire_4_time = constants[t4][0]* w * w * w/3 + constants[t4][1]* w * w/2 + constants[t4][2]* w;
                    time = tire_1_time+tire_2_time+tire_3_time+tire_4_time+pit_time_lost*3;
                    if(time <min){
                        min = time;
                        xf = x;
                        yf = y;
                        zf = z;
                        wf = w;
                    }
                }

            }
        }
        time=min;
        String type_and_compounds = "Three stop "+ compounds[t1]+"-"+compounds[t2]+"-"+compounds[t3]+"-"+compounds[t4];
        String pit_laps = xf+"-"+yf+"-"+zf+"-"+wf;
        return new String[]{type_and_compounds , pit_laps , String.valueOf(time)};
    }
}