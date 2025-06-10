import javafx.application.Application;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.layout.BorderPane;
import javafx.stage.Stage;
import org.jfree.chart.ChartFactory;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.fx.ChartViewer;
import org.jfree.chart.plot.PlotOrientation;
import org.jfree.data.category.DefaultCategoryDataset;

public class DoomWatchApp extends Application {
    private final DefaultCategoryDataset dataset = new DefaultCategoryDataset();
    private int counter = 0;

    private double callPython() {
        try {
            Process p = new ProcessBuilder("python", "bridge.py").start();
            java.io.BufferedReader reader = new java.io.BufferedReader(new java.io.InputStreamReader(p.getInputStream()));
            String line = reader.readLine();
            p.waitFor();
            if (line != null && line.contains("score")) {
                String[] parts = line.replace("{", "").replace("}", "").split(":");
                return Double.parseDouble(parts[1].split(",")[0]);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return 0.0;
    }

    @Override
    public void start(Stage stage) {
        stage.setTitle("Doom Watch");
        JFreeChart chart = ChartFactory.createLineChart(
                "Risk Skoru",
                "Gün",
                "Skor",
                dataset,
                PlotOrientation.VERTICAL,
                false,
                true,
                false);
        ChartViewer viewer = new ChartViewer(chart);

        Button update = new Button("Veriyi Güncelle");
        Label riskLabel = new Label("Risk: ?");
        update.setOnAction(ev -> {
            double score = callPython();
            dataset.addValue(score, "Risk", counter++);
            riskLabel.setText(String.format("Risk Skoru: %.2f", score));
            if (score > 0.75) {
                riskLabel.setStyle("-fx-text-fill: red;");
            } else {
                riskLabel.setStyle("-fx-text-fill: black;");
            }
        });

        BorderPane pane = new BorderPane();
        pane.setTop(update);
        pane.setCenter(viewer);
        pane.setBottom(riskLabel);
        stage.setScene(new Scene(pane, 800, 600));
        stage.show();
    }

    public static void main(String[] args) {
        launch(args);
    }
}
