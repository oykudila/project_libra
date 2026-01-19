<script>
    let status = "loading...";
    fetch("http://localhost:8000/health")
        .then((r) => r.json())
        .then((d) => (status = JSON.stringify(d)))
        .catch((e) => (status = "error: " + e.message));
</script>

<h1>Frontend is up</h1>
<p>Backend health: {status}</p>
