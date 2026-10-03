<script lang="ts">
  type Status = 'ready' | 'uploading' | 'done' | 'error';

  interface UploadItem {
    id: string;
    file: File;
    status: Status;
    progress: number;
    error?: string;
  }

  interface Props {
    endpoint?: string;
    accept?: string[]; // e.g. ['image/*', 'application/pdf']
    maxSizeMB?: number;
    maxFiles?: number;
  }

  let {
    endpoint = '/api/upload',
    accept = ['image/*', 'application/pdf'],
    maxSizeMB = 10,
    maxFiles = 5
  }: Props = $props();

  let items = $state<UploadItem[]>([]);
  let dragging = $state(false);
  let message = $state('');
  let input: HTMLInputElement;

  const pending = $derived(items.filter((i) => i.status === 'ready' || i.status === 'error'));
  const busy = $derived(items.some((i) => i.status === 'uploading'));

  function formatSize(bytes: number): string {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 ** 2) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / 1024 ** 2).toFixed(1)} MB`;
  }

  function matchesType(file: File): boolean {
    return accept.some((rule) =>
      rule.endsWith('/*') ? file.type.startsWith(rule.slice(0, -1)) : file.type === rule
    );
  }

  function addFiles(list: FileList | null) {
    if (!list) return;
    const problems: string[] = [];

    for (const file of Array.from(list)) {
      if (items.length >= maxFiles) {
        problems.push(`Only ${maxFiles} files are allowed.`);
        break;
      }
      if (!matchesType(file)) {
        problems.push(`${file.name} is not a supported file type.`);
        continue;
      }
      if (file.size > maxSizeMB * 1024 ** 2) {
        problems.push(`${file.name} is larger than ${maxSizeMB} MB.`);
        continue;
      }
      items.push({ id: crypto.randomUUID(), file, status: 'ready', progress: 0 });
    }

    message = problems.join(' ');
  }

  function onDrop(event: DragEvent) {
    event.preventDefault();
    dragging = false;
    addFiles(event.dataTransfer?.files ?? null);
  }

  function onChange(event: Event) {
    addFiles((event.currentTarget as HTMLInputElement).files);
    input.value = ''; // allow re-selecting the same file
  }

  function remove(id: string) {
    items = items.filter((i) => i.id !== id);
  }

  function uploadOne(item: UploadItem): Promise<void> {
    return new Promise((resolve) => {
      const body = new FormData();
      body.append('file', item.file);

      const xhr = new XMLHttpRequest();
      item.status = 'uploading';
      item.progress = 0;
      item.error = undefined;

      xhr.upload.onprogress = (e) => {
        if (e.lengthComputable) item.progress = Math.round((e.loaded / e.total) * 100);
      };
      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          item.status = 'done';
          item.progress = 100;
        } else {
          item.status = 'error';
          item.error = `Server responded with ${xhr.status}.`;
        }
        resolve();
      };
      xhr.onerror = () => {
        item.status = 'error';
        item.error = 'Network error. Check your connection and try again.';
        resolve();
      };

      xhr.open('POST', endpoint);
      xhr.send(body);
    });
  }

  async function uploadAll() {
    message = '';
    await Promise.all(pending.map(uploadOne));
  }
</script>

<section class="uploader">
  <div
    class="dropzone"
    class:dragging
    role="button"
    tabindex="0"
    aria-label="Choose files to upload"
    ondragover={(e) => {
      e.preventDefault();
      dragging = true;
    }}
    ondragleave={() => (dragging = false)}
    ondrop={onDrop}
    onclick={() => input.click()}
    onkeydown={(e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        input.click();
      }
    }}
  >
    <p class="headline">Drop files here or click to browse</p>
    <p class="hint">Up to {maxFiles} files, {maxSizeMB} MB each</p>
    <input
      bind:this={input}
      type="file"
      multiple
      accept={accept.join(',')}
      onchange={onChange}
      hidden
    />
  </div>

  {#if message}
    <p class="message" role="alert">{message}</p>
  {/if}

  {#if items.length}
    <ul class="files">
      {#each items as item (item.id)}
        <li class="file {item.status}">
          <div class="meta">
            <span class="name">{item.file.name}</span>
            <span class="size">{formatSize(item.file.size)}</span>
          </div>

          {#if item.status === 'uploading' || item.status === 'done'}
            <progress max="100" value={item.progress}></progress>
          {/if}

          <div class="state">
            {#if item.status === 'done'}
              <span class="badge ok">Uploaded</span>
            {:else if item.status === 'error'}
              <span class="badge err">{item.error}</span>
            {:else if item.status === 'uploading'}
              <span class="badge">{item.progress}%</span>
            {/if}

            <button
              class="remove"
              onclick={() => remove(item.id)}
              disabled={item.status === 'uploading'}
              aria-label="Remove {item.file.name}"
            >
              Remove
            </button>
          </div>
        </li>
      {/each}
    </ul>

    <button class="upload" onclick={uploadAll} disabled={busy || pending.length === 0}>
      {busy ? 'Uploading…' : `Upload ${pending.length} ${pending.length === 1 ? 'file' : 'files'}`}
    </button>
  {/if}
</section>

<style>
  .uploader {
    width: min(560px, 100%);
    display: grid;
    gap: 1rem;
  }

  .dropzone {
    border: 2px dashed var(--line);
    border-radius: var(--radius);
    background: var(--surface);
    padding: 2.5rem 1.5rem;
    text-align: center;
    cursor: pointer;
    transition:
      border-color 0.15s,
      background 0.15s;
  }

  .dropzone:hover,
  .dropzone.dragging {
    border-color: var(--accent);
    background: var(--accent-soft);
  }

  .headline {
    margin: 0;
    font-weight: 600;
  }

  .hint {
    margin: 0.25rem 0 0;
    color: var(--muted);
    font-size: 0.9rem;
  }

  .message {
    margin: 0;
    color: var(--error);
    font-size: 0.9rem;
  }

  .files {
    list-style: none;
    margin: 0;
    padding: 0;
    display: grid;
    gap: 0.5rem;
  }

  .file {
    display: grid;
    gap: 0.4rem;
    padding: 0.75rem 1rem;
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: var(--radius);
  }

  .file.error {
    border-color: var(--error);
  }

  .meta {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
  }

  .name {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-weight: 500;
  }

  .size {
    color: var(--muted);
    font-size: 0.85rem;
    flex-shrink: 0;
  }

  progress {
    width: 100%;
    height: 6px;
    accent-color: var(--accent);
  }

  .state {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 0.75rem;
    min-height: 1.5rem;
  }

  .badge {
    font-size: 0.85rem;
    color: var(--muted);
  }

  .badge.ok {
    color: var(--ok);
  }

  .badge.err {
    color: var(--error);
  }

  .remove {
    margin-left: auto;
    background: none;
    border: none;
    color: var(--muted);
    text-decoration: underline;
    padding: 0;
  }

  .remove:hover:not(:disabled) {
    color: var(--error);
  }

  .remove:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  .upload {
    padding: 0.75rem 1rem;
    border: none;
    border-radius: var(--radius);
    background: var(--accent);
    color: #fff;
    font-weight: 600;
  }

  .upload:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
</style>