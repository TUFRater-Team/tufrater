<script lang="ts">
  import type { PredictionResponse } from "../types";

  //same as :
  //const props = $props();
  //const onPrediction = props.onPrediction;
  let { onPrediction }: { onPrediction: (data: PredictionResponse) => void } =
    $props();

  let loading = $state(false);
  let errorMessage = $state("");

  async function handleFileChange(event: Event) {
    // check file before proceeding
    const input = event.target as HTMLInputElement;
    if (!input.files || input.files.length === 0) return;

    const file = input.files[0];
    const formData = new FormData();

    // FormData layout: label, value
    formData.append("file", file);

    loading = true;
    errorMessage = "";

    // request /files/upload
    try {
      const response = await fetch("http://localhost:8000/files/upload", {
        method: "POST",
        body: formData,
      });

      //if response returns HTTP status code 400-500 (error)
      if (!response.ok) {
        throw new Error("Failed to process file");
      }

      //proceed to send back the response from the backend to the parent
      const data: PredictionResponse = await response.json();
      onPrediction(data);
    } catch (error: any) {
      errorMessage = error.message;
    } finally {
      loading = false;
    }
  }
</script>

<div class="upload-container">
  <input type="file" onchange={handleFileChange} disabled={loading} />

  {#if loading}
    <p class="status">Analyzing level file...</p>
  {/if}

  {#if errorMessage}
    <p class="error">{errorMessage}</p>
  {/if}
</div>

<style>
  input[type="file"] {
    display: block;
    width: 100%;
    height: 6vh;
    padding: 1vh;
    color: #eee;
    font-family: sans-serif;
    font-size: 1rem;
    text-align: center;
    align-content: center;
    background-color: var(--surface);
    border: 2px dashed #ffffff;
    border-radius: 10px;
    cursor: pointer;
    position: relative;
    transition:
      background-color 0.2s ease,
      border-color 0.2s ease;
  }

  /* Hover state */
  input[type="file"]:hover:not(:disabled) {
    background-color: var(--surface);
    border-color: #0056b3;
  }

  /* Disabled state */
  input[type="file"]:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    background-color: var(--surface);
  }

  /* Hide the default browser file text/button */
  input[type="file"]::file-selector-button {
    display: none;
  }

  /* Custom text prompt inside the file input */
  input[type="file"]::before {
    content: "Drag & drop files here or click to browse";
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    width: 100%;
  }
</style>
