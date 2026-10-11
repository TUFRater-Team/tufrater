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
