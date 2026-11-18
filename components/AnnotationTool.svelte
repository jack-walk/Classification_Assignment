<script>
  import { onMount } from 'svelte';
  import './styles.css';

  let videos = [];
  let queue = [];
  let labels = [];
  let reviewer = '';
  let reviewerName = '';
  let currentIndex = 0;
  let isSetup = true;
  let isNameEntry = true;
  let isLoading = false;

  const SEED = 303;

  onMount(async () => {
    await loadVideos();
  });

  async function startAnnotation() {
    if (!reviewerName.trim()) {
      alert('Please enter your name');
      return;
    }
    reviewer = reviewerName;
    isNameEntry = false;
    queue = videos.slice();
  };

  async function loadVideos() {
    isLoading = true;
    try {
      const response = await fetch('./data/import/clean/all-briefings.csv');
      const text = await response.text();
      videos = parseCsv(text);
      shuffle(videos);
    } catch (error) {
      console.error('Error loading videos:', error);
    }
    isLoading = false;
  }

  function parseCsv(text) {
    const rows = [];
    let row = [],
      field = '',
      quoted = false;
    for (let i = 0; i < text.length; i++) {
      const c = text[i];
      if (quoted) {
        if (c === '"' && text[i + 1] === '"') {
          field += '"';
          i++;
        } else if (c === '"') {
          quoted = false;
        } else {
          field += c;
        }
      } else if (c === '"') {
        quoted = true;
      } else if (c === ',') {
        row.push(field);
        field = '';
      } else if (c === '\n') {
        row.push(field);
        rows.push(row);
        row = [];
        field = '';
      } else if (c !== '\r') {
        field += c;
      }
    }
    if (field || row.length) {
      row.push(field);
      rows.push(row);
    }
    const header = rows.shift();
    return rows.map((r) => Object.fromEntries(header.map((h, j) => [h, r[j]])));
  }

  function mulberry32(a) {
    return function () {
      a |= 0;
      a = (a + 0x6d2b79f5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = t + Math.imul(t ^ (t >>> 7), 61 | t) ^ t;
      return (((t ^ (t >>> 14)) >>> 0) / 4294967296);
    };
  }

  function shuffle(items) {
    const rand = mulberry32(SEED);
    for (let i = items.length - 1; i > 0; i--) {
      const j = Math.floor(rand() * (i + 1));
      [items[i], items[j]] = [items[j], items[i]];
    }
    return items;
  }

  function start() {
    if (!reviewer || videos.length === 0) return;
    queue = videos.map((v, idx) => ({ ...v, originalIndex: idx }));
    isSetup = false;
    currentIndex = 0;
  }

  function answer(value) {
    if (currentIndex >= queue.length) return;
    const video = queue[currentIndex];
    labels.push({
      video_id: video.video_id,
      contains_babydog_human: value,
      reviewer: reviewer
    });
    currentIndex++;
  }

  function undo() {
    if (labels.length === 0) return;
    labels.pop();
    currentIndex--;
  }

  function download() {
    const header = ['video_id', 'title', 'date', 'youtube_link', 'contains_babydog', 'interesting', 'reviewer', 'note'];
    const lines = [header.join(',')].concat(
      labels.map((l) => header.map((h) => csvCell(l[h])).join(','))
    );
    const csv = lines.join('\n') + '\n';
    const blob = new Blob([csv], { type: 'text/csv' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `${reviewer}.csv`;
    a.click();
    URL.revokeObjectURL(a.href);
  }

  function csvCell(value) {
    const s = String(value ?? '');
    return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
  }

  function handleKeydown(e) {
    if (isNameEntry) return;
    const key = e.key.toLowerCase();
    if (key === 'y') answer('True');
    if (key === 'n') answer('False');
    if (key === 's') answer('');
    if (key === 'b') undo();
  }

  $: currentVideo = queue[currentIndex];
  $: progress = `${labels.length + 1} of ${queue.length}`;
  $: isDone = currentIndex >= queue.length;
</script>

<svelte:window on:keydown={handleKeydown} />

<main>
  <h1>Seeing BabyDog?</h1>
  <p class="muted">Watch the video. Does Gov. Justice's bulldog, BabyDog, appear in this briefing?</p>

  {#if isNameEntry}
    <section id="name-entry">
      <div class="row">
        <input type="text" bind:value={reviewerName} placeholder="Enter your name" aria-label="Your name" />
        <button on:click={startAnnotation} disabled={!reviewerName || isLoading}>
          {isLoading ? 'Loading videos...' : 'Start Annotating'}
        </button>
      </div>
      <p class="muted" id="status">
        {isLoading ? 'Loading videos...' : `${videos.length} videos ready`}
      </p>
    </section>
  {:else if isDone}
    <p id="done">All videos labeled! Download your results.</p>
    <div class="row">
      <button on:click={download}>Download annotations (CSV)</button>
    </div>
  {:else if currentVideo}
    <section id="labeler">
      <p class="muted" id="progress">{progress} | {reviewer}</p>
      <div class="video">
        <iframe
          id="player"
          src="https://www.youtube.com/embed/{currentVideo.video_id}?rel=0"
          title="YouTube video"
          allow="encrypted-media"
          allowfullscreen
        />
      </div>
      <div class="info">
        <div id="text">{currentVideo.title}</div>
        <p class="muted" id="date">{currentVideo.date}</p>
      </div>
      <div class="row">
        <button class="true" on:click={() => answer('True')}>
          Yes <kbd>y</kbd>
        </button>
        <button class="false" on:click={() => answer('False')}>
          No <kbd>n</kbd>
        </button>
        <button on:click={() => answer('')}>
          Skip <kbd>s</kbd>
        </button>
        <button id="undo" on:click={undo}>
          Undo <kbd>b</kbd>
        </button>
      </div>
    </section>
  {/if}
</main>
