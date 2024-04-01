<script>
    import "../app.css";
    import Footer from "../components/Footer.svelte";
    import Navbar from "../components/Navbar.svelte";
</script>

<div class='min-h-screen flex flex-col justify-between'>
    <Navbar/>
    <div class='m-2 md:mx-auto md:w-[75%] my-5 h-full md:p-4 space-y-4'>
        <slot />
    </div>  
    <Footer/>
</div>