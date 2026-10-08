<script lang="ts">
  import FileUpload from './lib/FileUpload.svelte';

  // 1. Update the type definition to include the full feature set
  interface PredictionResponse {
    difficulty: string;
    raw_score: number;
    features: {
      tilecount: number;
      bpm: number;
      twirl_count: number;
      speed_change_count: number;
      s_norm: number;
      rt_score: number;
      p_var: number;
    };
  }

  // 2. Use the full interface for our reactive state
  let predictionResult = $state<PredictionResponse | null>(null);

  function handleNewPrediction(data: PredictionResponse) {
    predictionResult = data;
  }
</script>

<main class="container">
  <h1>TUFRater Upload </h1>

  <FileUpload onPrediction={handleNewPrediction} />

  <hr />

  <div class="result-box">
    {#if predictionResult}
      <!-- Main Results -->
      <h2>Results</h2>
      <p><strong>Difficulty Tier:</strong> {predictionResult.difficulty}</p>
      <p><strong>Raw Score:</strong> {predictionResult.raw_score.toFixed(2)}</p>

      <!-- Nested Feature Breakdown -->
      <h3>Features</h3>
      <ul class="features-list">
        <li><strong>Tile Count:</strong> {predictionResult.features.tilecount}</li>
        <li><strong>BPM:</strong> {predictionResult.features.bpm}</li>
        <li><strong>Twirl Count:</strong> {predictionResult.features.twirl_count}</li>
        <li><strong>Speed Changes:</strong> {predictionResult.features.speed_change_count}</li>
        <li><strong>Normalized S:</strong> {predictionResult.features.s_norm.toFixed(2)}</li>
        <li><strong>RT Score:</strong> {predictionResult.features.rt_score.toFixed(2)}</li>
        <li><strong>P Variance:</strong> {predictionResult.features.p_var.toFixed(2)}</li>
      </ul>
    {:else}
      <p class="placeholder">Upload a level file above to see its predicted difficulty.</p>
    {/if}
  </div>
</main>

<style>
  .container {
    max-width: 600px;
    margin: 3rem auto;
    background-color: var(--surface);
    font-family: sans-serif;
    padding: 0 1rem;
  }
  .placeholder {
    color: #888;
  }
  .features-list {
    list-style-type: none;
    padding: 0;
  }
  .features-list li {
    padding: 4px 0;
    border-bottom: 1px solid #eee;
  }
</style>