<h1>AgriTech Backend</h1>

<p>
The backend is built using Django and Django REST Framework. It handles
the project APIs, database operations, authentication, sensor data,
disease predictions, risk scores and treatment recommendations.
</p>

<h2>Project Structure</h2>

<pre>
agritech_backend/
│
├── agritech_backend/
│   ├── settings.py
│   └── urls.py
│
├── api/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── migrations/
│
├── disease_images/
└── manage.py
</pre>

<h3>Important Files</h3>

<ul>
  <li>
    <strong>models.py</strong> – Defines the database tables such as
    Farm, SensorNode, SensorReading, DiseasePrediction, RiskScore and
    TreatmentRecommendation.
  </li>
  <li>
    <strong>serializers.py</strong> – Converts model data into JSON and
    handles incoming API data.
  </li>
  <li>
    <strong>views.py</strong> – Contains the API logic and handles
    requests and responses.
  </li>
  <li>
    <strong>urls.py</strong> – Defines the API routes.
  </li>
  <li>
    <strong>settings.py</strong> – Contains Django, database, CORS and
    REST API configuration.
  </li>
  <li>
    <strong>migrations/</strong> – Contains database migration files.
  </li>
</ul>

<h2>API Endpoints</h2>

<h3>Authentication</h3>

<pre>
POST /api/token/
POST /api/token/refresh/
</pre>

<p>
JWT tokens are used for authentication. Protected APIs require an
access token in the request header.
</p>

<pre>
Authorization: Bearer &lt;access_token&gt;
</pre>

<h3>Farm & Sensor APIs</h3>

<pre>
/api/farms/
/api/sensors/
/api/readings/
</pre>

<p>
These APIs are used to create and manage farms, sensor nodes and
sensor readings.
</p>

<h3>Disease Prediction</h3>

<pre>
POST /api/predict/
</pre>

<p>
The frontend sends the captured leaf image to this endpoint.
The current endpoint accepts the image and processes the request;
actual ML model inference will be connected separately.
</p>

<h3>Risk Score</h3>

<pre>
/api/risk-scores/
</pre>

<p>
Provides stored risk-score records.
</p>

<p>
For a specific farm and disease:
</p>

<pre>
GET /api/risk-score/&lt;farm_id&gt;/&lt;disease&gt;/
</pre>

<p>
This endpoint returns the latest available risk score for the given
farm and disease.
</p>

<h3>Treatment Recommendations</h3>

<pre>
/api/treatments/
</pre>

<p>
Provides treatment recommendation data stored in the database.
</p>

<h3>Disease Prediction Records</h3>

<pre>
/api/predictions/
</pre>

<p>
Used to access stored disease prediction records.
</p>

<h2>How to Run</h2>

<p>Open the backend folder:</p>

<pre>
cd agritech_backend
</pre>

<p>Apply migrations:</p>

<pre>
python manage.py migrate
</pre>

<p>Start the server:</p>

<pre>
python manage.py runserver
</pre>

<p>The API will be available at:</p>

<pre>
http://127.0.0.1:8000/
</pre>

<h2>Current Status</h2>

<ul>
  <li>✅ Django and DRF setup</li>
  <li>✅ Database models and serializers</li>
  <li>✅ Farm, Sensor and Reading APIs</li>
  <li>✅ JWT authentication</li>
  <li>✅ Risk Score APIs</li>
  <li>✅ Image receiving through prediction API</li>
  <li>⏳ ML model inference integration</li>
  <li>⏳ Risk calculation module integration</li>
  <li>⏳ API documentation and staging deployment</li>
</ul>
