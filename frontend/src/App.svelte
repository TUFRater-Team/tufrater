<script lang="ts">
  import type { PredictionResponse } from "./types";
  import FileUpload from "./lib/FileUpload.svelte";

  // place to store the response from /files/upload
  let predictionResult = $state<PredictionResponse | null>(null);

  // function to change the predictionResult to FileUpload.svelte's data
  function handleNewPrediction(data: PredictionResponse) {
    predictionResult = data;
  }
</script>

<main class="container">
  <h1>TUFRater Upload</h1>

  <!-- when FileUpload returns data run the function handleNewPrediction -->
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
        <li>
          <strong>Tile Count:</strong>
          {predictionResult.features.tilecount}
        </li>
        <li><strong>BPM:</strong> {predictionResult.features.bpm}</li>
        <li>
          <strong>Twirl Count:</strong>
          {predictionResult.features.twirl_count}
        </li>
        <li>
          <strong>Speed Changes:</strong>
          {predictionResult.features.speed_change_count}
        </li>
        <li>
          <strong>Normalized S:</strong>
          {predictionResult.features.s_norm.toFixed(2)}
        </li>
        <li>
          <strong>RT Score:</strong>
          {predictionResult.features.rt_score.toFixed(2)}
        </li>
        <li>
          <strong>P Variance:</strong>
          {predictionResult.features.p_var.toFixed(2)}
        </li>
      </ul>
    {:else}
      <p class="placeholder">
        Upload a level file above to see its predicted difficulty.
      </p>
    {/if}
  </div>
</main>

<style>
  .container {
    max-width: 90vw;
    margin: 2vw;
    background-color: var(--surface);
    font-family: sans-serif;
    text-align: center;
    align-content: center;
    padding: 1vw;
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
