import '@babel/polyfill';

import GridSizeVariables from './components/grid-size-variables';
import HeaderDrawer from './components/header-drawer';
import SubMenu from './components/submenu';
import BackLink from './components/back-link';
import MobileSubMenu from './components/mobile-sub-menu';
import CookieWarning from './components/cookie-message';
import Accordion from './components/accordion';
import Carousel from './components/carousel';
import SquareCarousel from './components/carousel-square';
import LogoCarousel from './components/carousel-logo';
import Slideshow from './components/slideshow';
import VideoModal from './components/video-modal';
import RelatedContent from './components/related-content';
import Tabs from './components/tabs';
import Sticky from './components/position-sticky-event';
import ActualHeight from './components/actual-height';
import ProjectFilters from './components/project-filters';
import AnchorNav from './components/anchor-nav';
import SitewideAlert from './components/sitewide-alert';
import './components/sticky-header';
import './components/lazyload-images';
import './components/outdated-banner';
import './components/home-menu';
import './components/stats-block';
import './components/parallax';
import './components/modal';
import './components/sticky-point';

import '../sass/main.scss';

document.addEventListener('DOMContentLoaded', () => {
    /* eslint-disable no-new, no-restricted-syntax */

    // GridSizeVariables first to ensure custom properites are populated
    for (const gridVariables of document.querySelectorAll(
        GridSizeVariables.selector(),
    )) {
        new GridSizeVariables(gridVariables);
    }

    const cookie = document.querySelector(CookieWarning.selector());
    new CookieWarning(cookie);

    for (const sitewideAlert of document.querySelectorAll(
        SitewideAlert.selector(),
    )) {
        new SitewideAlert(sitewideAlert);
    }

    for (const accordion of document.querySelectorAll(Accordion.selector())) {
        new Accordion(accordion);
    }

    for (const carousel of document.querySelectorAll(Carousel.selector())) {
        new Carousel(carousel);
    }

    for (const squareCarousel of document.querySelectorAll(
        SquareCarousel.selector(),
    )) {
        new SquareCarousel(squareCarousel);
    }

    for (const logoCarousel of document.querySelectorAll(
        LogoCarousel.selector(),
    )) {
        new LogoCarousel(logoCarousel);
    }

    for (const slideshow of document.querySelectorAll(Slideshow.selector())) {
        new Slideshow(slideshow);
    }

    for (const headerdrawer of document.querySelectorAll(
        HeaderDrawer.selector(),
    )) {
        new HeaderDrawer(headerdrawer);
    }

    for (const backlink of document.querySelectorAll(BackLink.selector())) {
        new BackLink(backlink);
    }

    for (const submenu of document.querySelectorAll(SubMenu.selector())) {
        new SubMenu(submenu);
    }

    for (const relatedcontent of document.querySelectorAll(
        RelatedContent.selector(),
    )) {
        new RelatedContent(relatedcontent);
    }

    for (const mobilesubmenu of document.querySelectorAll(
        MobileSubMenu.selector(),
    )) {
        new MobileSubMenu(mobilesubmenu);
    }

    // Toggle subnav visibility
    for (const subnavBack of document.querySelectorAll('[data-subnav-back]')) {
        subnavBack.addEventListener('click', () => {
            subnavBack.parentNode.classList.remove('is-visible');
        });
    }

    for (const videomodal of document.querySelectorAll(VideoModal.selector())) {
        new VideoModal(videomodal);
    }

    for (const projectfilters of document.querySelectorAll(
        ProjectFilters.selector(),
    )) {
        new ProjectFilters(projectfilters);
    }

    for (const tabs of document.querySelectorAll(Tabs.selector())) {
        new Tabs(tabs);
    }

    for (const sticky of document.querySelectorAll(Sticky.selector())) {
        new Sticky(sticky);
    }

    for (const anchornav of document.querySelectorAll(AnchorNav.selector())) {
        new AnchorNav(anchornav);
    }

    new ActualHeight();
});
