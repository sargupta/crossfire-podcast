'use client';

import dynamic from 'next/dynamic';

const PodcastPlayer = dynamic(() => import('@/components/PodcastPlayer'), {
  ssr: false,
});

export default function Home() {
  return (
    <main className="h-screen w-screen overflow-hidden bg-black">
      <PodcastPlayer initialTopic="Future of Artificial Intelligence" />
    </main>
  );
}
