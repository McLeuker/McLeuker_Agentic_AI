'use client';

import { TopNavigation } from "@/components/layout/TopNavigation";
import { Footer } from "@/components/layout/Footer";

export default function MentionsLegalesPage() {
  return (
    <div className="min-h-screen bg-[#070707] flex flex-col">
      <TopNavigation variant="marketing" />

      <main className="pt-24 pb-16 flex-1">
        <div className="container mx-auto px-6">
          <div className="max-w-3xl mx-auto">
            <h1 className="font-editorial text-4xl md:text-5xl text-white mb-6">
              Mentions L&eacute;gales
            </h1>
            <p className="text-white/50 mb-12">
              Derni&egrave;re mise &agrave; jour : 6 f&eacute;vrier 2026
            </p>

            <div className="space-y-10">
              <section>
                <h2 className="text-xl font-medium text-white mb-4">&Eacute;diteur du site</h2>
                <div className="space-y-2 text-white/60 leading-relaxed">
                  <p><strong className="text-white/80">Raison sociale :</strong> McLeuker AI (micro-entreprise / en cours d&apos;immatriculation)</p>
                  <p><strong className="text-white/80">Repr&eacute;sentant l&eacute;gal :</strong> Qigen Lin</p>
                  <p><strong className="text-white/80">Adresse :</strong> Paris, France</p>
                  <p><strong className="text-white/80">Email :</strong>{' '}
                    <a href="mailto:contact@mcleuker.com" className="text-white/80 underline hover:text-white">contact@mcleuker.com</a>
                  </p>
                  <p><strong className="text-white/80">SIRET :</strong> En cours d&apos;immatriculation</p>
                  <p><strong className="text-white/80">TVA intracommunautaire :</strong> En cours d&apos;obtention</p>
                </div>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">Directeur de la publication</h2>
                <p className="text-white/60 leading-relaxed">
                  Qigen Lin &mdash;{' '}
                  <a href="mailto:contact@mcleuker.com" className="text-white/80 underline hover:text-white">contact@mcleuker.com</a>
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">H&eacute;bergement</h2>
                <div className="space-y-2 text-white/60 leading-relaxed">
                  <p><strong className="text-white/80">H&eacute;bergeur du site web (frontend) :</strong> Vercel Inc.</p>
                  <p>440 N Barranca Ave #4133, Covina, CA 91723, &Eacute;tats-Unis</p>
                  <p><a href="https://vercel.com" target="_blank" rel="noopener noreferrer" className="text-white/80 underline hover:text-white">https://vercel.com</a></p>
                </div>
                <div className="space-y-2 text-white/60 leading-relaxed mt-4">
                  <p><strong className="text-white/80">H&eacute;bergeur du backend :</strong> Railway Corp.</p>
                  <p>San Francisco, CA, &Eacute;tats-Unis</p>
                  <p><a href="https://railway.app" target="_blank" rel="noopener noreferrer" className="text-white/80 underline hover:text-white">https://railway.app</a></p>
                </div>
                <div className="space-y-2 text-white/60 leading-relaxed mt-4">
                  <p><strong className="text-white/80">Base de donn&eacute;es et authentification :</strong> Supabase Inc.</p>
                  <p>San Francisco, CA, &Eacute;tats-Unis</p>
                  <p><a href="https://supabase.com" target="_blank" rel="noopener noreferrer" className="text-white/80 underline hover:text-white">https://supabase.com</a></p>
                </div>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">D&eacute;l&eacute;gu&eacute; &agrave; la Protection des Donn&eacute;es (DPO)</h2>
                <p className="text-white/60 leading-relaxed">
                  Qigen Lin (r&eacute;f&eacute;rent RGPD) &mdash;{' '}
                  <a href="mailto:dpo@mcleuker.com" className="text-white/80 underline hover:text-white">dpo@mcleuker.com</a>
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">Propri&eacute;t&eacute; intellectuelle</h2>
                <p className="text-white/60 leading-relaxed">
                  L&apos;ensemble du contenu de ce site (textes, graphismes, logos, ic&ocirc;nes, images, clips audio et vid&eacute;o, logiciels) est la propri&eacute;t&eacute; de McLeuker AI ou de ses conc&eacute;dants de licence et est prot&eacute;g&eacute; par les lois fran&ccedil;aises et internationales relatives &agrave; la propri&eacute;t&eacute; intellectuelle. Toute reproduction, repr&eacute;sentation, modification ou adaptation, totale ou partielle, est interdite sans autorisation pr&eacute;alable &eacute;crite.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">Donn&eacute;es personnelles</h2>
                <p className="text-white/60 leading-relaxed">
                  Pour en savoir plus sur la mani&egrave;re dont nous collectons et traitons vos donn&eacute;es personnelles, veuillez consulter notre{' '}
                  <a href="/privacy" className="text-white/80 underline hover:text-white">Politique de Confidentialit&eacute;</a>.
                  Conform&eacute;ment au R&egrave;glement G&eacute;n&eacute;ral sur la Protection des Donn&eacute;es (RGPD) et &agrave; la Loi Informatique et Libert&eacute;s, vous disposez de droits d&apos;acc&egrave;s, de rectification, de suppression et de portabilit&eacute; de vos donn&eacute;es. Vous pouvez exercer ces droits en contactant{' '}
                  <a href="mailto:dpo@mcleuker.com" className="text-white/80 underline hover:text-white">dpo@mcleuker.com</a>{' '}
                  ou en utilisant notre{' '}
                  <a href="/legal/dsar" className="text-white/80 underline hover:text-white">formulaire de demande d&apos;exercice de droits</a>.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">Cookies</h2>
                <p className="text-white/60 leading-relaxed">
                  Ce site utilise des cookies. Pour en savoir plus, consultez notre{' '}
                  <a href="/cookies" className="text-white/80 underline hover:text-white">Politique de Cookies</a>.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-medium text-white mb-4">Droit applicable et juridiction</h2>
                <p className="text-white/60 leading-relaxed">
                  Les pr&eacute;sentes mentions l&eacute;gales sont r&eacute;gies par le droit fran&ccedil;ais. En cas de litige, les tribunaux de Paris seront seuls comp&eacute;tents, sous r&eacute;serve des dispositions imp&eacute;ratives du Code de la consommation relatives &agrave; la comp&eacute;tence juridictionnelle.
                </p>
              </section>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
