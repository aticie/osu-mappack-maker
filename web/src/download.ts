export const downloadWithHref = (data: Blob, name?: string) => {
  const element = document.createElement("a");
  const href = URL.createObjectURL(data);

  let x = href.split("/");
  let hrefTitle = x[x.length - 1];
  
  element.setAttribute("href", href);
  element.setAttribute("download", name || hrefTitle);

  element.click();
  URL.revokeObjectURL(href);
}
