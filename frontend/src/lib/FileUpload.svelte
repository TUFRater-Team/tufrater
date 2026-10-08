<script lang="ts">
  // 1. Ensure this matches your actual backend response completely
  export interface PredictionResponse {
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

  let { onPrediction }: { onPrediction: (data: PredictionResponse) => void } = $props();

  let loading = $state(false);
  let errorMessage = $state("");

  async function handleFileChange(event: Event) {
    const input = event.target as HTMLInputElement;
    if (!input.files || input.files.length === 0) return;

    const file = input.files[0];
    const formData = new FormData();
    formData.append("file", file);

    loading = true;
    errorMessage = "";

    try {
      const response = await fetch("http://localhost:8000/files/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to process file on the backend.");
      }

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