from flask import Flask, render_template, request, redirect, url_for, send_file
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error
from fpdf import FPDF
import os

app = Flask(__name__)

data_frame = None
model = None
training_stats = {}
plots = []
data_description = ""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    global data_frame
    file = request.files['file']
    if file:
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)
        data_frame = pd.read_csv(file_path)
        data_description = data_frame.describe().to_string()
        return render_template('result.html', data_description=data_description, columns=data_frame.columns.tolist())
    return redirect(url_for('index'))

@app.route('/analyze', methods=['POST'])
def analyze():
    global data_description
    if data_frame is not None:
        data_description = data_frame.describe().to_string()
        return render_template('result.html', data_description=data_description, columns=data_frame.columns.tolist())
    return redirect(url_for('index'))

@app.route('/visualize', methods=['POST'])
def visualize():
    global plots
    if data_frame is not None:
        sns.pairplot(data_frame)
        plt.savefig("static/pairplot.png")
        plots.append("static/pairplot.png")
        return send_file("static/pairplot.png", mimetype='image/png')
    return redirect(url_for('index'))

@app.route('/train', methods=['POST'])
def train():
    global model, training_stats
    if data_frame is not None:
        selected_features = request.form.getlist('features')
        target_column = request.form['target']
        if not selected_features:
            return redirect(url_for('index'))
        features = data_frame[selected_features]
        target = data_frame[target_column]
        X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)
        model = LinearRegression()
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)
        mse = mean_squared_error(y_test, predictions)
        mae = mean_absolute_error(y_test, predictions)
        training_stats = {
            "MSE": mse,
            "MAE": mae,
            "Coefficients": model.coef_,
            "Intercept": model.intercept_
        }
        formula = f"{target_column} = " + " + ".join([f"{coef}*{feat}" for coef, feat in zip(model.coef_, selected_features)]) + f" + {model.intercept_}"
        return render_template('result.html', training_stats=training_stats, formula=formula, columns=data_frame.columns.tolist())
    return redirect(url_for('index'))

@app.route('/export_pdf', methods=['POST'])
def export_pdf():
    global training_stats, data_description, plots
    file_path = "static/report.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Forecast Alpha - Model Training Report", ln=True, align='C')
    pdf.cell(200, 10, txt="Training Statistics:", ln=True, align='L')
    for key, value in training_stats.items():
        pdf.cell(200, 10, txt=f"{key}: {value}", ln=True, align='L')
    pdf.cell(200, 10, txt="Predictive Formula:", ln=True, align='L')
    formula = f"{request.form['target']} = " + " + ".join([f"{coef}*{feat}" for coef, feat in zip(model.coef_, request.form.getlist('features'))]) + f" + {model.intercept_}"
    pdf.multi_cell(0, 10, txt=formula)
    
    # Add data description to PDF
    pdf.add_page()
    pdf.cell(200, 10, txt="Data Description:", ln=True, align='L')
    pdf.multi_cell(0, 10, txt=data_description)
    
    # Add plots to PDF
    for plot in plots:
        pdf.add_page()
        pdf.image(plot, x=10, y=10, w=pdf.w - 20)
    
    pdf.output(file_path)
    return send_file(file_path, as_attachment=True)

@app.route('/export_excel', methods=['POST'])
def export_excel():
    global training_stats, data_frame, plots
    file_path = "static/report.xlsx"
    with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
        # Export coefficients
        coeffs = pd.DataFrame({
            "Feature": request.form.getlist('features'),
            "Coefficient": model.coef_
        })
        coeffs.to_excel(writer, sheet_name='Coefficients', index=False)

        # Export training stats
        stats_df = pd.DataFrame(list(training_stats.items()), columns=["Metric", "Value"])
        stats_df.to_excel(writer, sheet_name='Training Stats', index=False)

        # Export predictive formula
        formula = f"{request.form['target']} = " + " + ".join([f"{coef}*{feat}" for coef, feat in zip(model.coef_, request.form.getlist('features'))]) + f" + {model.intercept_}"
        formula_df = pd.DataFrame({"Predictive Formula": [formula]})
        formula_df.to_excel(writer, sheet_name='Predictive Formula', index=False)

        # Export data description
        description_df = pd.DataFrame(data_frame.describe())
        description_df.to_excel(writer, sheet_name='Data Description')

        # Export plots
        for plot in plots:
            worksheet = writer.book.add_worksheet('Plot')
            worksheet.insert_image('A1', plot)
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)