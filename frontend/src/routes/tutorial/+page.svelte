<script>
    import Cards from '../../components/Cards.svelte';
    import data from '$lib/tutorial.json';
</script>

<div>
    <h1 class='my-8 text-3xl font-bold'>How to record a (good) video</h1>
    <Cards cards_data={data.record_video_cards} />
    <h1 class='my-8 text-3xl font-bold'>How to upload a video (or mesh)</h1>
    <Cards cards_data={data.upload_video_cards} />
    <h1 class='my-4 text-3xl font-bold'>How to edit or update Khachkar data</h1>
    <Cards cards_data={data.update_data_cards} />
</div>