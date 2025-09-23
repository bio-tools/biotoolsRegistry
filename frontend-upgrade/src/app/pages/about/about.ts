import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatDividerModule } from '@angular/material/divider';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-about',
  imports: [
    CommonModule,
    MatCardModule,
    MatIconModule,
    MatDividerModule
  ],
  templateUrl: './about.html',
  styleUrl: './about.scss'
})
export class About {
  aboutItems = [
    {
      icon: 'public',
      title: 'Open Data',
      text: `<em>bio.tools</em> content is freely available under 
             <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank">CC BY 4.0</a> license 
             - you are free to share and adapt the data, so long as you give credit and do not restrict the freedom of others.`
    },
    {
      icon: 'code',
      title: 'Open Source',
      text: `<em>bio.tools</em> source code is freely available under 
             <a href="http://www.gnu.org/licenses/gpl-3.0.html" target="_blank">GPL-3.0</a> - 
             you are free to share and adapt our software, but you must ensure it remains free for all its users.`
    },
    {
      icon: 'groups',
      title: 'Built by You',
      text: `We depend on the goodwill and enthusiasm of our thousands (and growing!) of contributors - if you develop or provide tools and online services, 
             please <a href="/register">add</a> them after <a href="/signup">signing-up</a>.`
    },
    {
      icon: 'link',
      title: 'Tool IDs',
      text: `All <em>bio.tools</em> entries are assigned a human-friendly unique identifier, <em>e.g.</em> <a href="/signalp" target="_blank">biotools:signalp</a>.  
             Once verified, a <em>bio.tools</em> ID provides a stable way to trace resources and integrate <em>bio.tools</em> data with other projects.`
    },
    {
      icon: 'book',
      title: 'Standard Semantics',
      text: `The scientific function of <em>bio.tools</em> resources can be precisely annotated in defined terms from the 
             <a href="http://github.com/edamontology/edamontology/" target="_blank">EDAM ontology</a>, including common topics, operations, types of 
             data and data formats.`
    },
    {
      icon: 'edit',
      title: 'Standard Syntax',
      text: `<em>bio.tools</em> resource descriptions adhere to a rigorous syntax defined by 
             <a href="http://github.com/bio-tools/biotoolsschema" target="_blank">biotoolsSchema</a>, which provides regular expressions, 
             controlled vocabularies and other syntax rules for 50 key attributes.`
    },
    {
      icon: 'circle',
      title: 'Community-driven',
      text: `We rely upon <a href="https://www.elixir-europe.org/communities" target="_blank">scientific communities</a> to improve the terminology and 
             description of resources in different domains of the life sciences - we welcome your help with this 
             <a href="https://biotools.readthedocs.io/en/latest/editors_guide.html" target="_blank">work in progress</a>.`
    },
    {
      icon: 'science',
      title: 'Backed by ELIXIR',
      text: `<em>bio.tools</em> is anchored within <a href="https://www.elixir-europe.org/" target="_blank">ELIXIR</a>, the European Infrastructure 
             for Biological Information. <em>bio.tools</em> will remain free, open and maintained in the long term.`
    },
    {
      icon: 'dashboard',
      title: 'Tools Platform',
      text: `<em>bio.tools</em> is an integral part of the <a href="https://www.elixir-europe.org/platforms/tools" target="_blank">ELIXIR Tools Platform</a>,
             enabling the development, description, discovery, re-use, deployment and benchmarking of software tools and workflows.`
    },
    {
      icon: 'api',
      title: 'API',
      text: `Our Web API provides an easy way to access the <em>bio.tools</em> data, allowing precise or alternatively flexible queries over all fields.  
             Please see the <a href="https://biotools.readthedocs.io/en/latest/api_reference.html" target="_blank">API reference</a> and
             <a href="https://biotools.readthedocs.io/en/latest/api_usage_guide.html" target="_blank">API Usage Guide</a>.`
    },
    {
      icon: 'description',
      title: 'Documentation',
      text: `Check out the docs for <a href="https://biotools.readthedocs.io/en/latest/" target="_blank">bio.tools</a>, 
             <a href="https://biotoolsschema.readthedocs.io/en/latest/" target="_blank">biotoolsSchema</a> and the 
             <a href="https://edamontologydocs.readthedocs.io/en/latest/" target="_blank">EDAM ontology</a> - report any problems or make suggestions via GitHub.`
    },
    {
      icon: 'help',
      title: 'Support',
      text: `Whether you are a user of <em>bio.tools</em>, a developer who wants to add their tools, or a scientist who wants integrate our data with your own; 
             help is at hand. Head over to <a href="http://github.com/bio-tools/biotoolsregistry/" target="_blank">GitHub</a> or 
             <a href="mailto:support-bio-tools@sdu.dk">mail us</a> directly.`
    }
  ];

  flags = [
    { img: '/img/countries/be.svg', label: 'Belgium', link: 'https://www.elixir-europe.org/about-us/who-we-are/nodes/belgium' },
    { img: '/img/countries/cz.svg', label: 'Czech Republic', link: 'https://www.elixir-europe.org/about-us/who-we-are/nodes/czech-republic' },
    { img: '/img/countries/dk.svg', label: 'Denmark', link: 'https://www.elixir-europe.org/about-us/who-we-are/nodes/denmark' },
    { img: '/img/countries/ee.svg', label: 'Estonia', link: 'http://www.elixir-europe.org/about-us/who-we-are/nodes/estonia' },
    { img: '/img/countries/fi.svg', label: 'Finland', link: 'https://www.elixir-europe.org/about-us/who-we-are/nodes/finland' },
    { img: '/img/countries/fr.svg', label: 'France', link: 'https://www.elixir-europe.org/about-us/who-we-are/nodes/france' },
    { img: '/img/countries/de.svg', label: 'Germany', link: 'https://www.elixir-europe.org/about-us/who-we-are/nodes/germany' },
    { img: '/img/countries/gr.svg', label: 'Greece', link: 'https://www.elixir-europe.org/about-us/who-we-are/nodes/greece' },
    { img: '/img/countries/hu.svg', label: 'Hungary', link: 'https://www.elixir-europe.org/about-us/who-we-are/nodes/hungary' },
    { img: '/img/countries/ie.svg', label: 'Ireland', link: 'https://www.elixir-europe.org/about-us/who-we-are/nodes/ireland' },
    { img: '/img/countries/il.svg', label: 'Israel', link: 'http://www.elixir-europe.org/about-us/who-we-are/nodes/israel' },
    { img: '/img/countries/it.svg', label: 'Italy', link: 'http://www.elixir-europe.org/about-us/who-we-are/nodes/italy' },
    { img: '/img/countries/lu.svg', label: 'Luxembourg', link: 'http://www.elixir-europe.org/about-us/who-we-are/nodes/luxembourg' },
    { img: '/img/countries/nl.svg', label: 'Netherlands', link: 'http://www.elixir-europe.org/about-us/who-we-are/nodes/netherlands' },
    { img: '/img/countries/no.svg', label: 'Norway', link: 'http://www.elixir-europe.org/about-us/who-we-are/nodes/norway' },
    { img: '/img/countries/pt.svg', label: 'Portugal', link: 'http://www.elixir-europe.org/about-us/who-we-are/nodes/portugal' },
    { img: '/img/countries/si.svg', label: 'Slovenia', link: 'http://www.elixir-europe.org/about-us/who-we-are/nodes/slovenia' },
    { img: '/img/countries/es.svg', label: 'Spain', link: 'http://www.elixir-europe.org/about-us/who-we-are/nodes/spain' },
    { img: '/img/countries/se.svg', label: 'Sweden', link: 'http://www.elixir-europe.org/about-us/who-we-are/nodes/sweden' },
    { img: '/img/countries/ch.svg', label: 'Switzerland', link: 'http://www.elixir-europe.org/about-us/who-we-are/nodes/switzerland' },
    { img: '/img/countries/gb.svg', label: 'United Kingdom', link: 'http://www.elixir-europe.org/about-us/who-we-are/nodes/uk' },
    { img: '/img/countries/cy.svg', label: 'Cyprus', link: 'https://www.elixir-europe.org/about-us/who-we-are/nodes/cyprus' },
    { img: '/img/countries/embl.png', label: 'EMBL', link: 'https://www.elixir-europe.org/about-us/who-we-are/nodes/embl-ebi' }
  ];
}
