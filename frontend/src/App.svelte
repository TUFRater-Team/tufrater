<script lang="ts">
  import FileUpload from './lib/FileUpload.svelte';
</script>

<main>
  <h1>Upload files</h1>
  <p class="intro">Add images or PDFs, then select Upload.</p>
  <FileUpload endpoint="/api/upload" accept={['image/*', 'application/pdf']} maxSizeMB={10} maxFiles={5} />
</main>

<style>
  main {
    width: min(560px, 100%);
  }

  .intro {
    margin: 0 0 1.5rem;
    color: var(--muted);
  }
</style>