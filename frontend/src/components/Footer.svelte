<script>
    import { Footer, FooterBrand, FooterLink, FooterLinkGroup } from 'flowbite-svelte';
    import { MUSEUM_URL, ONLINE_MUSEUM_URL } from '$lib/constants';
</script>

<div class='align-bottom h-full'>
    <Footer footerType="logo">
        <div class="sm:flex sm:items-center sm:justify-between">
            <FooterBrand href="/" src="/favicon.png" alt="Crowdsourcing app Logo" name="Crowdsourcing app" />
        </div>
        <hr class="my-6 border-gray-200 sm:mx-auto dark:border-gray-700 lg:my-8" />
        <FooterLinkGroup ulClass="flex flex-wrap items-center mb-6 text-sm text-gray-500 sm:mb-0 dark:text-gray-400">
            <FooterLink href={MUSEUM_URL}>Museum</FooterLink>
            <FooterLink href={ONLINE_MUSEUM_URL}>Online Museum</FooterLink>
        </FooterLinkGroup>
    </Footer>
</div>