import Link from "next/link";

interface SectionItem {
  href: string;
  title: string;
  description: string;
}

interface SectionGridProps {
  heading: string;
  items: SectionItem[];
}

export default function SectionGrid({ heading, items }: SectionGridProps) {
  return (
    <section className="section-block">
      <header className="section-head">
        <h1>{heading}</h1>
      </header>
      <div className="card-grid">
        {items.map((item) => (
          <Link href={item.href} key={item.href} className="link-card reveal">
            <h2>{item.title}</h2>
            <p>{item.description}</p>
          </Link>
        ))}
      </div>
    </section>
  );
}
