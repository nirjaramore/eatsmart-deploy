import Head from 'next/head'
import SiteHeader from '../components/SiteHeader'

export default function About() {
    return (
        <>
            <Head>
                <title>About Us - EatSmart</title>
                <meta name="viewport" content="width=device-width, initial-scale=1" />
            </Head>
            <main style={{ background: 'var(--brand-bg)', color: '#eca6a4', minHeight: '100vh', paddingBottom: '48px' }}>
                <SiteHeader active="about" />

                <section style={{ maxWidth: '1100px', margin: '0 auto', padding: '96px 24px 0' }}>
                    <div style={{ width: '100%', maxWidth: '900px', margin: '0 auto', fontFamily: "'Baloo 2', Inter, sans-serif", lineHeight: 1.6, textAlign: 'justify' }}>
                    <p style={{ fontSize: '2.5rem', marginBottom: '1rem', fontWeight: 'bold', textAlign: 'center', color: '#e27575' }}>
                        ever stared at a food label and felt... nothing?<br />
                        same. we did too.
                    </p>
                    <p style={{ marginBottom: '1rem' }}>
                        85% of us check brand names, but only 20% actually read ingredients. just 18% of Gen Z consistently reads labels even though 58% buy packaged food regularly. we're out here trusting vibes over facts.
                    </p>
                    <p style={{ marginBottom: '1rem' }}>
                        the problem? labels can be misleading even with strict FSSAI norms—"sugar-free" loaded with fats, "real fruit" juices with 10% actual fruit. most of us find nutrition info either too confusing or too cramped.
                    </p>
                    <p style={{ fontSize: '1.1rem', fontWeight: 'bold', marginBottom: '1rem', color: '#e27575' }}>
                        so we're building something different.
                    </p>

                    <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1rem', color: '#e27575' }}>what we're doing</h2>
                    <p style={{ marginBottom: '1rem' }}>
                        eatsmartly is a community fixing India's nutrition information gap—one product at a time.
                    </p>
                    <p style={{ marginBottom: '1rem' }}>
                        we're building a database of underrated, actually-healthy Indian brands. the ones hiding on bottom shelves. the local heroes nobody talks about.
                    </p>
                    <p style={{ marginBottom: '1rem' }}>
                        but here's the thing: we need you.
                    </p>

                    <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1rem', color: '#e27575' }}>how you help</h2>
                    <p style={{ marginBottom: '1rem' }}>
                        spot a healthy product? upload one pic. literally just one.
                    </p>
                    <ul style={{ marginBottom: '1rem', paddingLeft: '1.5rem' }}>
                        <li>that millet snack from your hometown store</li>
                        <li>the organic dal brand your mom swears by</li>
                        <li>the chemical-free masala you just discovered</li>
                    </ul>
                    <p style={{ marginBottom: '1rem' }}>
                        one image = better info for everyone
                    </p>
                    <p style={{ marginBottom: '1rem' }}>
                        we're crowdsourcing what big brands won't tell you. think of it as wikipedia, but for not getting fooled by food labels.
                    </p>

                    <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1rem' }}>what's coming</h2>
                    <p style={{ marginBottom: '1rem' }}>
                        once we've got the data (with your help), we're launching an app that:
                    </p>
                    <ul style={{ marginBottom: '1rem', paddingLeft: '1.5rem' }}>
                        <li>scans barcodes, shows real nutrition</li>
                        <li>suggests better alternatives based on your allergies/preferences</li>
                        <li>builds personalized diet plans that actually work for Indian eating</li>
                    </ul>
                    <p style={{ marginBottom: '1rem' }}>
                        no BS. no hidden sugars marketed as "health drinks." just real data, real choices.
                    </p>

                    <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1rem', color: '#e27575' }}>join the build</h2>
                    <p style={{ marginBottom: '1rem' }}>
                        this only works if we're in it together.
                    </p>
                    <p style={{ marginBottom: '1rem' }}>
                        upload. share. spread the word.
                    </p>
                    <p style={{ fontSize: '1.1rem', fontWeight: 'bold', color: '#e27575' }}>
                        because knowing what you're eating shouldn't require a chemistry degree.
                    </p>
                    </div>
                </section>
            </main>
        </>
    )
}