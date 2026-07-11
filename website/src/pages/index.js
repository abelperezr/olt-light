import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import Layout from '@theme/Layout';
import Translate from '@docusaurus/Translate';
import styles from './index.module.css';

const cards = [
  {
    icon: '⌨️',
    title: <Translate id="home.card.cli.title">eCLI modular</Translate>,
    text: <Translate id="home.card.cli.text">Añade comandos, contextos y completado sin tocar la plataforma base.</Translate>,
    to: '/docs/how-to/customize-ecli',
  },
  {
    icon: '🌐',
    title: <Translate id="home.card.dhcp.title">ONU DHCP</Translate>,
    text: <Translate id="home.card.dhcp.text">Personaliza la emulación DHCPv4 y DHCPv6 de los suscriptores.</Translate>,
    to: '/docs/how-to/customize-dhcp',
  },
  {
    icon: '📡',
    title: <Translate id="home.card.telemetry.title">Optics e IPFIX</Translate>,
    text: <Translate id="home.card.telemetry.text">Controla diagnósticos ópticos y registros de telemetría sintética.</Translate>,
    to: '/docs/how-to/customize-optics',
  },
  {
    icon: '🧱',
    title: <Translate id="home.card.overlay.title">Overlay seguro</Translate>,
    text: <Translate id="home.card.overlay.text">Extiende imágenes precompiladas sin publicar YANG, seeds de fábrica o device extensions.</Translate>,
    to: '/docs/explanation/public-overlay',
  },
];

function Home() {
  return (
    <Layout title="Light OLT" description="Public customization layer for Light OLT">
      <header className={clsx('hero', styles.hero)}>
        <div className="container">
          <p className={styles.eyebrow}>LIGHT OLT CUSTOMIZATION LAYER</p>
          <h1 className={styles.title}>
            <Translate id="home.title">Personaliza el comportamiento. Conserva la plataforma.</Translate>
          </h1>
          <p className={styles.subtitle}>
            <Translate id="home.subtitle">Un overlay público para adaptar eCLI, DHCP de ONUs, óptica e IPFIX sobre una imagen OLT estable.</Translate>
          </p>
          <div className={styles.actions}>
            <Link className="button button--primary button--lg" to="/docs/tutorials/first-build">
              <Translate id="home.start">Comenzar</Translate>
            </Link>
            <Link className="button button--secondary button--outline button--lg" to="/docs/explanation/architecture">
              <Translate id="home.architecture">Ver arquitectura</Translate>
            </Link>
          </div>
        </div>
      </header>
      <main className={styles.main}>
        <div className="container">
          <section className={styles.grid}>
            {cards.map((card) => (
              <Link className={styles.card} to={card.to} key={card.to}>
                <span className={styles.icon}>{card.icon}</span>
                <h2>{card.title}</h2>
                <p>{card.text}</p>
              </Link>
            ))}
          </section>
          <section className={styles.command}>
            <div>
              <p className={styles.eyebrow}>THREE COMMANDS</p>
              <h2><Translate id="home.quick.title">De código a contenedor</Translate></h2>
            </div>
            <pre><code>{`./build.sh check\n./build.sh\ndocker compose -f examples/docker-compose.yml up -d`}</code></pre>
          </section>
        </div>
      </main>
    </Layout>
  );
}

export default Home;
