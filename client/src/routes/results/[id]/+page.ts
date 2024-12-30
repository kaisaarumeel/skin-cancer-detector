// Contributors:
// * Contributor: <kaisa.arumeel@gmail.com>
// * Contributor: <elindstr@student.chalmers.se>
import type { PageLoad } from './$types';

export const prerender = false;
export const ssr = false;

export const load: PageLoad = ({ params }) => {
  return {
    id: params.id
  };
}